import streamlit as st
import json
import os
import random

# 数据存储文件
DATA_FILE = "stamps_data.json"

# 游戏配置字典
GAMES = {
    "touhu": "🎯 趣味投壶",
    "wudu": "🦂 射五毒",
    "caimi": "🏮 端午猜谜",
    "wucaisheng": "🧶 五彩绳手作"
}


# 加载数据
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# 保存数据
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    st.set_page_config(page_title="端午轻游园打卡", page_icon="🐉", layout="centered")

    # 获取 URL 参数
    query_params = st.query_params
    game_id = query_params.get("game", None)
    is_admin = query_params.get("admin", None)

    data = load_data()

    # ---------------- 兑奖核销端 ----------------
    if is_admin == "true":
        st.title("🎁 奖品兑换核销台")
        st.write("工作人员专用：输入学号后点击查询")

        # 初始化 session_state 来记忆查询状态
        if 'queried_id' not in st.session_state:
            st.session_state.queried_id = ""

        student_id = st.text_input("请输入核销学号：")

        # 独立的查询按钮，点击后把学号存入记忆
        if st.button("🔍 查询进度"):
            if student_id:
                st.session_state.queried_id = student_id
            else:
                st.warning("⚠️ 请先输入学号！")

        # 只要当前输入的学号和记忆中的学号匹配，就一直展示结果（完美避开嵌套冲突）
        if st.session_state.queried_id == student_id and student_id != "":
            if student_id in data:
                stamps = data[student_id]

                # 过滤掉抽奖标记，只计算真正的游戏通关印章
                game_stamps = [s for s in stamps if s in GAMES]
                stamp_count = len(game_stamps)

                st.success(f"✅ 学号 {student_id} 已集齐 {stamp_count} 枚印章！")
                st.write("**已通关项目：**")
                for s in game_stamps:
                    st.write(f"- {GAMES.get(s, s)}")

                st.divider()
                st.subheader("兑奖提示：")

                # 按照策划书设定的阶梯奖励
                if stamp_count >= 4:
                    st.info("✨ 满足条件：可参与【幸运奖】抽奖！")

                    # 设定库存总数
                    TOTAL_FAN = 4
                    TOTAL_CUP = 4

                    # 统计已经抽出的奖品数量
                    drawn_fans = sum(1 for items in data.values() if "prize_fan" in items)
                    drawn_cups = sum(1 for items in data.values() if "prize_cup" in items)

                    # 防重复抽奖校验
                    if "has_drawn" in stamps:
                        st.write("---")
                        st.success("🎯 该同学已完成抽奖。")

                        if "prize_fan" in stamps:
                            st.write("### 🎁 抽奖结果：🍃 无叶小风扇")
                        elif "prize_cup" in stamps:
                            st.write("### 🎁 抽奖结果：💧 大容量水杯")
                        else:
                            st.write("### 🎁 抽奖结果：再接再厉（未中幸运奖）")

                    else:
                        # 现在的抽奖按钮可以安全地触发了
                        if st.button("🎲 点击抽取幸运大奖"):
                            pool = ["谢谢参与"]
                            weights = [60]

                            if drawn_fans < TOTAL_FAN:
                                pool.append("🍃 小风扇")
                                weights.append(20)

                            if drawn_cups < TOTAL_CUP:
                                pool.append("💧 大容量水杯")
                                weights.append(20)

                            result = random.choices(pool, weights=weights, k=1)[0]
                            data[student_id].append("has_drawn")

                            if result == "🍃 小风扇":
                                data[student_id].append("prize_fan")
                            elif result == "💧 大容量水杯":
                                data[student_id].append("prize_cup")

                            save_data(data)
                            st.rerun()

                elif stamp_count >= 3:
                    st.success("🎉 满足条件：可兑换【进阶奖】！")
                elif stamp_count >= 2:
                    st.warning("🎈 满足条件：可兑换【参与奖】！")
                else:
                    st.error("集章数量不足，还需继续努力哦！")
            else:
                st.error("❌ 未查询到该学号的打卡记录。")

    # ---------------- 玩家打卡端 ----------------
    elif game_id in GAMES:
        st.title(f"{GAMES[game_id]} - 扫码打卡")
        st.write("恭喜通关！请输入你的学号完成打卡：")

        student_id = st.text_input("请输入学号：", key=f"input_{game_id}")

        if st.button("确认打卡"):
            if student_id:
                if student_id not in data:
                    data[student_id] = []

                if game_id in data[student_id]:
                    st.warning("⚠️ 你已经在这个项目打过卡啦，去挑战其他游戏吧！")
                else:
                    data[student_id].append(game_id)
                    save_data(data)

                    # 计算当前真实印章数
                    current_stamps = [s for s in data[student_id] if s in GAMES]
                    st.success(f"🎉 打卡成功！目前已集齐 {len(current_stamps)} 枚印章。")
            else:
                st.error("学号不能为空！")

    # ---------------- 默认欢迎页 ----------------
    else:
        st.title("🐉 端午轻游园电子集章系统")
        st.info("👈 请使用微信扫描各个游戏点位桌面的专属二维码进行打卡。")


if __name__ == "__main__":
    main()