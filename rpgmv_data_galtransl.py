import argparse
import os
import time
import json

from tprtools import jsonpath

"""
requirements:
thiliapr-tools
"""

__version__ = "1.0"


class RPGMakerMVData:
	@staticmethod
	def event(event: jsonpath.JSONObject, parent_path: str) -> list[str] | None:
		try:
			if event["code"] == 102:
				return [jsonpath.concat_path(parent_path, f"$.parameters[0][{i}]") for i in range(len(event["parameters"][0])) if event["parameters"][0][i]]
			elif event["code"] == 401:
				return [jsonpath.concat_path(parent_path, "$.parameters[0]")] if event["parameters"][0] else []
			else:
				return
		except KeyError as e:
			e.add_note(f"Event; path={parent_path}:\n" + json.dumps(event) + "\n" + "-" * 16)
			raise e

	@staticmethod
	def common_events(events: list) -> list[str]:
		messages: list[str] = []
		for common_event_index in range(len(events)):
			common_event = events[common_event_index]
			if common_event is None:
				continue

			for event_index in range(len(common_event["list"])):
				event = common_event["list"][event_index]

				message = RPGMakerMVData.event(event, f"$[{common_event_index}].list[{event_index}]")
				if message:
					messages += message

		return messages

	@staticmethod
	def items(items: list) -> list[str]:
		messages: list[str] = []
		for item_index in range(len(items)):
			item = items[item_index]
			if item is None:
				continue
			if not item.get("description"):
				continue

			messages.append(f"$[{item_index}].description")

		return messages

	@staticmethod
	def map_events(map_events: dict) -> list[str]:
		messages: list[str] = []

		try:
			for map_event_index in range(len(map_events["events"])):
				map_event = map_events["events"][map_event_index]
				if map_event is None:
					continue

				try:
					for page_index in range(len(map_event["pages"])):
						page = map_event["pages"][page_index]

						for event_index in range(len(page["list"])):
							event = page["list"][event_index]

							event_messages = RPGMakerMVData.event(event, f"$.events[{map_event_index}].pages[{page_index}].list[{event_index}]")
							if event_messages:
								messages += event_messages
				except KeyError as e:
					e.add_note(f"Map Event; path={f'$.events[{event_index}]'}:\n{json.dumps(event)}\n" + "-" * 16)
					raise e
		except KeyError as e:
			e.add_note(f"Map:\n{json.dumps(map_events)}\n" + "-" * 16)
			raise e

		return messages


def log(at: str, message: str, verbose: bool = False) -> None:
	message = message.replace("\n", "\\n").replace("\\", "\\\\")

	if verbose:
		print(time.strftime("[%Y-%m-%d] [%H:%M:%S]"), f"[{at}]", "[verbose]", message)
	else:
		print(time.strftime("[%Y-%m-%d] [%H:%M:%S]"), f"[{at}]", message)


def extract_script(data_path: str, output_path: str, verbose: bool = False):
	# Read data files from data path
	log("ScriptExtractor", f"Loading Data...")

	data_files = {}
	for filename in os.listdir(data_path):
		if not filename.endswith(".json"):
			continue
		if filename == "System.json":
			continue

		if verbose:
			log("ScriptExtractor", f"Loading {filename}", verbose=True)

		with open(os.path.join(data_path, filename), mode="r", encoding="utf-8") as f:
			data_files[filename] = json.load(f)

	log("ScriptExtractor", f"Loaded data.")

	# Scan messages to translate
	log("ScriptExtractor", f"Extracting Data...")

	messages: dict[str, list[str]] = {}
	for filename, data in data_files.items():
		if verbose:
			log("ScriptExtractor", f"Extracting {filename}", verbose=True)

		if filename == "CommonEvents.json":
			messages[filename] = [{"path": message_path, "message": jsonpath.get(data, message_path)} for message_path in RPGMakerMVData.common_events(data)]
		elif isinstance(data, list):
			messages[filename] = [{"path": message_path, "message": jsonpath.get(data, message_path)} for message_path in RPGMakerMVData.items(data)]
		elif isinstance(data, dict):
			messages[filename] = [{"path": message_path, "message": jsonpath.get(data, message_path)} for message_path in RPGMakerMVData.map_events(data)]

	log("ScriptExtractor", f"Extracted data.")

	# Remove empty JSONObjects in messages
	messages = {message_file: file_messages for message_file, file_messages in messages.items() if file_messages}

	if verbose:
		log("ScriptExtractor", f"Scripts: {list(messages.keys())}", verbose=True)

	# Export messages to rpgmaker scripts
	log("ScriptExtractor", f"Start to Export Scripts")
	for filename, message_paths in messages.items():
		if verbose:
			log("ScriptExtractor", f"Exporting {filename}", verbose=True)

		with open(os.path.join(output_path, filename), encoding="utf-8", mode="w") as f:
			json.dump(message_paths, f, indent="\t", ensure_ascii=False)

	log("ScriptExtractor", f"Exported scripts.")


def generate_galtransl_script(script_path: str, output_path: str, verbose: bool = False):
	# Read data files from data path
	log("GalTranslScriptGenerator", f"Loading Data...")

	script_files = {}
	for filename in os.listdir(script_path):
		if not filename.endswith(".json"):
			continue

		if verbose:
			log("GalTranslScriptGenerator", f"Loading {filename}", verbose=True)

		with open(os.path.join(script_path, filename), mode="r", encoding="utf-8") as f:
			script_files[filename] = json.load(f)

	log("GalTranslScriptGenerator", f"Loaded data.")

	# To GalTransl Script
	scripts = {filename: [{"message": message["message"]} for message in messages] for filename, messages in script_files.items()}

	if verbose:
		log("GalTranslScriptGenerator", f"Scripts: {list(scripts.keys())}", verbose=True)

	# Export scripts to GalTransl Scripts
	log("GalTranslScriptGenerator", f"Start to Export Scripts.")
	for filename, context in scripts.items():
		if verbose:
			log("GalTranslScriptGenerator", f"Exporting {filename}", verbose=True)

		with open(os.path.join(output_path, filename), encoding="utf-8", mode="w") as f:
			json.dump(context, f, indent="\t", ensure_ascii=False)

	log("GalTranslScriptGenerator", f"Exported scripts.")


def apply_script(data_path: str, rpgmaker_script_path: str, galtransl_script_path: str, output_path: str, verbose: bool = False):
	# Read data files from data path
	log("GalTranslScriptApplicator", f"Loading Data...")

	data_files, rpgmaker_scripts, galtransl_scripts = [dict() for _ in range(3)]
	for filename in os.listdir(rpgmaker_script_path):
		if not filename.endswith(".json"):
			continue

		if verbose:
			log("GalTranslScriptGenerator", f"Loading {filename}", verbose=True)

		with open(os.path.join(data_path, filename), mode="r", encoding="utf-8") as f:
			data_files[filename] = json.load(f)
		with open(os.path.join(rpgmaker_script_path, filename), mode="r", encoding="utf-8") as f:
			rpgmaker_scripts[filename] = json.load(f)
		with open(os.path.join(galtransl_script_path, filename), mode="r", encoding="utf-8") as f:
			galtransl_scripts[filename] = json.load(f)

	log("GalTranslScriptApplicator", f"Loaded data.")

	# Merge translation and path
	rpgmaker_translations = {
		filename: [rpgmaker_message | translation_message for rpgmaker_message, translation_message in zip(rpgmaker_messages, translation_messages)]
		for filename, rpgmaker_messages, translation_messages in zip(rpgmaker_scripts.keys(), rpgmaker_scripts.values(), galtransl_scripts.values())
	}

	# Source -> Destination
	log("GalTranslScriptApplicator", f"Source -> Destination...")
	[jsonpath.assign(data, message_info["path"], message_info["message"]) for filename, data in data_files.items() for message_info in rpgmaker_translations[filename]]
	log("GalTranslScriptApplicator", f"Source -> Destination is OK.")

	# Export Files
	log("GalTranslScriptApplicator", f"Start to Export Scripts.")
	for filename, context in data_files.items():
		if verbose:
			log("GalTranslScriptApplicator", f"Exporting {filename}", verbose=True)

		with open(os.path.join(output_path, filename), encoding="utf-8", mode="w") as f:
			json.dump(context, f, indent="\t", ensure_ascii=False)

	log("GalTranslScriptApplicator", f"Exported scripts.")


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("action", choices=["extract_script", "generate_galtransl_script", "apply_script"], help="Action")
	parser.add_argument("-d", "--data", help="Game Data Path (extract_script, apply_script)")
	parser.add_argument("-s", "--rpgmaker-script", help="RPGMaker Script Path (generate_galtransl_script, apply_script)")
	parser.add_argument("-g", "--galtransl-script", help="GalTransl Script Path (apply_script)")
	parser.add_argument("-o", "--output", default="output/", help="Output Path (ALL)")
	parser.add_argument("-v", "--verbose", action="store_true", default=False)
	parser.add_argument("-V", "--version", action="version", version=__version__, help="Show version")
	args = parser.parse_args()

	if args.action == "extract_script":
		extract_script(args.data, args.output, args.verbose)
	elif args.action == "generate_galtransl_script":
		generate_galtransl_script(args.rpgmaker_script, args.output, args.verbose)
	elif args.action == "apply_script":
		apply_script(args.data, args.rpgmaker_script, args.galtransl_script, args.output, args.verbose)


if __name__ == '__main__':
	main()
