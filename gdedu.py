import json
from argparse import ArgumentParser
from typing import Any

import requests


Content_Type = "application/x-www-form-urlencoded; charset=UTF-8"


def 基本API调用(api: str, 方法: str, 数据: dict, HHCSRFToken: str, jsessionid: str) -> dict[str, Any]:
    r = requests.request(method=方法, url=api, data=数据, headers={"Content-Type": Content_Type, "HHCSRFToken": HHCSRFToken}, cookies={"JSESSIONID": jsessionid})
    if r.status_code != 200:
        e = Exception((f"服务器返回 {r.status_code} 状态码。"))
        e.add_note(f"API={api}; 方法={方法}; 数据={数据}")
        e.add_note(r.content.decode())
        raise e
    else:
        try:
            return json.loads(r.content)
        except json.JSONDecodeError as e:
            e.add_note("服务器返回非 JSON 格式信息。")
            e.add_note(f"API={api}; 方法={方法}; 数据={数据}")
            e.add_note(r.content.decode())
            raise e


def 获取重要观测点(配置: dict[str, str]) -> list[dict[str, str]]:
    原始数据 = 基本API调用("https://czzp.gdedu.gov.cn/czzhszpj/web/formsNav/xsCltbIndex.do?method=queryZbTxList", "get", "", **配置)
    重要观测点 = []

    for 分类1 in 原始数据["xsbtxList"]:
        for 分类2 in 分类1["erjizblist"]:
            for 观测点项目 in 分类2["sanjizblist"]:
                重要观测点.append({"分类1": 分类1["zbmc"], "分类2": 分类2["zb2mc"], "注释": 观测点项目["tbsm"], "id": 观测点项目["tbxsz_id"]})

    return 重要观测点


def 获取记录(观测点的ID: str, 配置: dict[str, str]) -> list[str, Any]:
    原始数据 = 基本API调用(
        "https://czzp.gdedu.gov.cn/czzhszpj/web/forms/zhszTyl.do", "post",
        f"method=queryZhszTylList&sfDqXnXq=1&tbxszId={观测点的ID}",
        **配置)
    记录 = []

    for 记录项目 in 原始数据["rows"]:
        记录.append({"主题": 记录项目["ztnr"], "描述": 记录项目["ms"], "证明人": 记录项目["zmr"], "id": 记录项目["id"]})

    return 记录


def 填报观测点(观测点的ID: str, 主题: str, 描述: str, 证明人: str, 选入档案: bool, 配置: dict[str, str]) -> bool:
    原始数据 = 基本API调用(
        "https://czzp.gdedu.gov.cn/czzhszpj/web/forms/zhszTyl.do", "post",
        f"method=saveZhszTyl&ztnr={主题}&ms={描述}&zmr={证明人}&zt={int(选入档案)}&tbxszId={观测点的ID}",
        **配置)
    return 原始数据


def main():
    参数解析器 = ArgumentParser(description="重要观测点自动填写程序。适用于广东省初中学生综合素质评价信息管理系统。")
    参数解析器.add_argument("-i", "--jsession-id", required=True, dest="jsessionid")
    参数解析器.add_argument("-t", "--hhcsrf-token", required=True, dest="HHCSRFToken")
    参数解析器.add_argument("-c", "--certifier", required=True, dest="certifier")
    参数 = 参数解析器.parse_args()

    # 配置
    HHCSRFToken = 参数.HHCSRFToken
    jsessionid = 参数.jsessionid
    证明人 = 参数.certifier

    配置: dict[str, str] = {"HHCSRFToken": HHCSRFToken, "jsessionid": jsessionid}
    print("信息:", f"HHCSRFToken={HHCSRFToken}", f"JSESSIONID={jsessionid}", f"证明人={证明人}", "", sep="\n    ")

    # 获取重要观测点
    重要观测点: list[dict[str, str]] = 获取重要观测点(配置)

    # 获取记录
    for 观测点项目 in 重要观测点:
        if (记录 := 获取记录(观测点项目["id"], 配置)) != []:
            print(f"观测点记录: {观测点项目['分类2']} - {观测点项目['注释']} - {记录[0]['主题']}")
            continue

        print(f"填报观测点: {观测点项目['分类2']} - {观测点项目['注释']}")
        填报观测点(观测点项目["id"], "空缺", "空缺", 证明人, False, 配置)


if __name__ == '__main__':
    main()
