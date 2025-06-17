import streamlit as st
import random
import time

# --- アプリの基本設定 ---
st.set_page_config(
    page_title="🃏 カイジ Eカード",
    page_icon="👑",
    layout="centered",
    initial_sidebar_state="auto"
)

st.title("🃏 カイジ Eカード 心理戦！ 🃏")
st.markdown("皇帝側か奴隷側かを選んで、AI（コンピュータ）と勝負しよう！")

# --- カードの定義 ---
EMPEROR = "皇帝👑"
CITIZEN = "市民🧍"
SLAVE = "奴隷⛓️"

# 勝敗ルール (自分が出すカード: 相手が出すカード -> 勝敗)
# 1: 勝ち, 0: 引き分け, -1: 負け
RULES = {
    EMPEROR: {CITIZEN: 1, SLAVE: -1, EMPEROR: 0},
    CITIZEN: {SLAVE: 1, EMPEROR: -1, CITIZEN: 0},
    SLAVE: {EMPEROR: 1, CITIZEN: -1, SLAVE: 0},
}

# 初期手札
HANDS = {
    "皇帝側": {EMPEROR: 1, CITIZEN: 4, SLAVE: 0},
    "奴隷側": {EMPEROR: 0, CITIZEN: 4, SLAVE: 1},
}

# ゲーム設定
MAX_ROUNDS = 5 # 5回戦 (今回はスコアで終了するため、この値は「最大ラウンド」として機能します)
WINNING_SCORE = 1 # 勝敗を決めるスコア

# --- セッションステートの初期化 ---
if 'player_side' not in st.session_state:
    st.session_state.player_side = None
if 'player_hand' not in st.session_state:
    st.session_state.player_hand = {}
if 'ai_hand' not in st.session_state:
    st.session_state.ai_hand = {}
if 'player_score' not in st.session_state:
    st.session_state.player_score = 0
if 'ai_score' not in st.session_state:
    st.session_state.ai_score = 0
if 'current_round' not in st.session_state:
    st.session_state.current_round = 0
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'round_result_message' not in st.session_state:
    st.session_state.round_result_message = ""
if 'last_player_card' not in st.session_state:
    st.session_state.last_player_card = None
if 'last_ai_card' not in st.session_state:
    st.session_state.last_ai_card = None
if 'countdown_active' not in st.session_state:
    st.session_state.countdown_active = False
if 'display_round_result' not in st.session_state:
    st.session_state.display_round_result = False


# --- ヘルパー関数 ---
def reset_game():
    """ゲームの状態をリセットする"""
    st.session_state.player_side = None
    st.session_state.player_hand = {}
    st.session_state.ai_hand = {}
    st.session_state.player_score = 0
    st.session_state.ai_score = 0
    st.session_state.current_round = 0
    st.session_state.game_started = False
    st.session_state.round_result_message = ""
    st.session_state.last_player_card = None
    st.session_state.last_ai_card = None
    st.session_state.countdown_active = False
    st.session_state.display_round_result = False
    st.rerun()

def get_hand_display(hand_dict):
    """手札を文字列で表示するヘルパー関数"""
    display_str = ""
    for card, count in hand_dict.items():
        if count > 0:
            display_str += f"{card} x {count} "
    return display_str.strip()

def ai_choose_card(ai_current_hand, player_side):
    """AIがカードを選択するロジック（市民を選ぶ確率を少し上げた版）"""
    available_cards = [card for card, count in ai_current_hand.items() if count > 0]

    if not available_cards:
        return None

    # 市民を選ぶための重み付きリストを作成
    weighted_choices = []
    for card, count in ai_current_hand.items():
        if count > 0:
            if card == CITIZEN:
                # 市民カードの確率を高くする（例: 3倍の重み）
                weighted_choices.extend([card] * (count * 3))
            else:
                weighted_choices.extend([card] * count)
    
    # 重み付きリストからランダムに選択
    if weighted_choices:
        return random.choice(weighted_choices)
    else:
        # 万が一weighted_choicesが空になった場合（理論上は起こらないはずですが念のため）
        return random.choice(available_cards)

def play_round_logic(player_card):
    """1ラウンドのゲームのロジックを実行する（UI更新は含まない）"""
    st.session_state.last_player_card = player_card
    
    ai_card = ai_choose_card(st.session_state.ai_hand, st.session_state.player_side)
    
    if ai_card is None:
        st.session_state.round_result_message = "AIがカードを出せなくなりました。ゲームをリセットしてください。"
        st.session_state.game_started = False
        st.session_state.display_round_result = True
        return

    st.session_state.last_ai_card = ai_card

    st.session_state.player_hand[player_card] -= 1
    st.session_state.ai_hand[ai_card] -= 1

    player_result = RULES[player_card][ai_card]

    if st.session_state.player_side == "皇帝側":
        if player_result == 1:
            st.session_state.player_score += 1
            outcome_message_side = "皇帝側の勝利！🎊"
        elif player_result == -1:
            st.session_state.ai_score += 1
            outcome_message_side = "奴隷側の勝利！💀"
        else:
            outcome_message_side = "引き分け！🤝"
    else: # プレイヤーは奴隷側
        if player_result == 1:
            st.session_state.player_score += 1
            outcome_message_side = "奴隷側の勝利！🎊"
        elif player_result == -1:
            st.session_state.ai_score += 1
            outcome_message_side = "皇帝側の勝利！💀"
        else:
            outcome_message_side = "引き分け！🤝"

    st.session_state.round_result_message = f"あなたは **{player_card}**、AIは **{ai_card}** を出しました。{outcome_message_side}"
    st.session_state.current_round += 1
    
    st.session_state.display_round_result = True

def proceed_to_next_round():
    """次のラウンドへ進む、またはゲームを終了する"""
    st.session_state.display_round_result = False
    if st.session_state.player_score >= WINNING_SCORE or \
       st.session_state.ai_score >= WINNING_SCORE or \
       st.session_state.current_round >= MAX_ROUNDS:
        st.session_state.game_started = False
    st.rerun()

# --- UIの構築 ---

# ゲーム開始前
if not st.session_state.game_started:
    st.subheader("どちらの側でプレイしますか？")
    col_emperor, col_slave = st.columns(2)
    with col_emperor:
        if st.button("皇帝側を選ぶ👑", use_container_width=True):
            st.session_state.player_side = "皇帝側"
            st.session_state.ai_side = "奴隷側"
            st.session_state.player_hand = HANDS["皇帝側"].copy()
            st.session_state.ai_hand = HANDS["奴隷側"].copy()
            st.session_state.game_started = True
            st.session_state.countdown_active = True
            st.session_state.current_round = 0
            st.session_state.player_score = 0
            st.session_state.ai_score = 0
            st.session_state.display_round_result = False
            st.rerun()
    with col_slave:
        if st.button("奴隷側を選ぶ⛓️", use_container_width=True):
            st.session_state.player_side = "奴隷側"
            st.session_state.ai_side = "皇帝側"
            st.session_state.player_hand = HANDS["奴隷側"].copy()
            st.session_state.ai_hand = HANDS["皇帝側"].copy()
            st.session_state.game_started = True
            st.session_state.countdown_active = True
            st.session_state.current_round = 0
            st.session_state.player_score = 0
            st.session_state.ai_score = 0
            st.session_state.display_round_result = False
            st.rerun()
else: # ゲーム進行中
    if st.session_state.countdown_active:
        st.subheader("ゲーム開始までお待ちください...")
        countdown_placeholder = st.empty()
        for i in range(3, 0, -1):
            countdown_placeholder.markdown(f"## **{i}**")
            time.sleep(1)
        countdown_placeholder.markdown("## **勝負！**")
        time.sleep(0.5)
        st.session_state.countdown_active = False
        st.rerun()
    elif st.session_state.display_round_result:
        st.header(f"--- 第 {st.session_state.current_round} 回戦 結果 ---")
        st.subheader(f"あなたの役割: {st.session_state.player_side}")
        st.markdown(f"**スコア**: あなた ({st.session_state.player_side}): {st.session_state.player_score} vs AI ({st.session_state.ai_side}): {st.session_state.ai_score}")
        st.info(st.session_state.round_result_message)
        st.write(f"前回のあなたの手: {st.session_state.last_player_card}, 前回のAIの手: {st.session_state.last_ai_card}")

        if st.session_state.player_score >= WINNING_SCORE or \
           st.session_state.ai_score >= WINNING_SCORE or \
           st.session_state.current_round >= MAX_ROUNDS:
            st.header("--- ゲーム終了！ ---")
            if st.session_state.player_score > st.session_state.ai_score:
                winning_side = st.session_state.player_side
                st.balloons()
                st.success(f"🎉 **{winning_side}** の勝利です！ 🎉")
                st.write(f"最終スコア: あなた ({st.session_state.player_side}): {st.session_state.player_score} vs AI ({st.session_state.ai_side}): {st.session_state.ai_score}")
            elif st.session_state.player_score < st.session_state.ai_score:
                winning_side = st.session_state.ai_side
                st.error(f"残念... **{winning_side}** の勝利です。💀")
                st.write(f"最終スコア: あなた ({st.session_state.player_side}): {st.session_state.player_score} vs AI ({st.session_state.ai_side}): {st.session_state.ai_score}")
                st.image("https://media.tenor.com/images/30b91e92c286d9c614b80a373b526685/tenor.gif", caption="ざわ…ざわ…", width=200)
            else:
                st.warning(f"引き分けです！🤝")
                st.write(f"最終スコア: あなた ({st.session_state.player_side}): {st.session_state.player_score} vs AI ({st.session_state.ai_side}): {st.session_state.ai_score}")
            st.button("もう一度プレイする", on_click=reset_game, type="primary")
        else:
            st.button("次のラウンドへ！", on_click=proceed_to_next_round, type="primary")
    else: # ゲーム継続中 (カウントダウンもラウンド結果表示も終了)
        st.header(f"--- 第 {st.session_state.current_round + 1} 回戦 ---")
        st.subheader(f"あなたの役割: {st.session_state.player_side}")

        # スコア表示
        st.markdown(f"**スコア**: あなた ({st.session_state.player_side}): {st.session_state.player_score} vs AI ({st.session_state.ai_side}): {st.session_state.ai_score}")

        # 手札表示
        st.subheader("あなたの手札:")
        st.write(get_hand_display(st.session_state.player_hand))

        st.subheader("カードを選択してください:")
        
        cols = st.columns(len(st.session_state.player_hand))
        
        available_cards_to_play = [card for card, count in st.session_state.player_hand.items() if count > 0]
        
        for i, card in enumerate([EMPEROR, CITIZEN, SLAVE]): # 表示順序を固定
            if card in available_cards_to_play:
                with cols[i]:
                    if st.button(f"出す: {card}", key=f"play_{card}"):
                        play_round_logic(card)
            else:
                with cols[i]:
                    st.button(f"出す: {card}", key=f"play_{card}_disabled", disabled=True)

st.markdown("---")
st.markdown("© 2024 カイジ Eカードアプリ (Inspired by Kaiji Ultimate Survivor)")
