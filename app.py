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
MAX_ROUNDS = 5 # 5回戦

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
    st.rerun()

def get_hand_display(hand_dict):
    """手札を文字列で表示するヘルパー関数"""
    display_str = ""
    for card, count in hand_dict.items():
        if count > 0:
            display_str += f"{card} x {count} "
    return display_str.strip()

def ai_choose_card(ai_current_hand, player_side):
    """AIがカードを選択するロジック（簡易版）"""
    available_cards = [card for card, count in ai_current_hand.items() if count > 0]

    # AIの役割に応じて戦略を少し変える
    if player_side == "皇帝側": # AIは奴隷側
        # 奴隷側は皇帝に勝つ奴隷カードを温存しつつ市民を消費
        if SLAVE in available_cards and ai_current_hand[SLAVE] > 0 and st.session_state.current_round >= MAX_ROUNDS - 1: # 終盤で奴隷を出す
             return SLAVE
        if CITIZEN in available_cards and ai_current_hand[CITIZEN] > 0:
            return CITIZEN
        if SLAVE in available_cards and ai_current_hand[SLAVE] > 0: # 市民がない場合、奴隷を出す
            return SLAVE

    else: # AIは皇帝側
        # 皇帝側は奴隷に負ける皇帝カードを温存しつつ市民を消費
        if EMPEROR in available_cards and ai_current_hand[EMPEROR] > 0 and st.session_state.current_round >= MAX_ROUNDS - 1: # 終盤で皇帝を出す
             return EMPEROR
        if CITIZEN in available_cards and ai_current_hand[CITIZEN] > 0:
            return CITIZEN
        if EMPEROR in available_cards and ai_current_hand[EMPEROR] > 0: # 市民がない場合、皇帝を出す
            return EMPEROR

    # どれもなければ残ってるカードからランダム
    return random.choice(available_cards)


def play_round(player_card):
    """1ラウンドのゲームをプレイする"""
    st.session_state.last_player_card = player_card
    
    # AIがカードを選択
    ai_card = ai_choose_card(st.session_state.ai_hand, st.session_state.player_side)
    st.session_state.last_ai_card = ai_card

    # 手札から使用したカードを減らす
    st.session_state.player_hand[player_card] -= 1
    st.session_state.ai_hand[ai_card] -= 1

    player_result = RULES[player_card][ai_card] # プレイヤー視点での結果

    outcome_message = ""
    if player_result == 1:
        st.session_state.player_score += 1
        outcome_message = "あなたの勝ち！🎊"
    elif player_result == -1:
        st.session_state.ai_score += 1
        outcome_message = "AIの勝ち！💀"
    else:
        outcome_message = "引き分け！🤝"
    
    # 役割に応じたメッセージ
    if st.session_state.player_side == "皇帝側":
        if player_result == 1:
            outcome_message = "皇帝側の勝利！🎊"
        elif player_result == -1:
            outcome_message = "奴隷側の勝利！💀"
    else: # プレイヤーは奴隷側
        if player_result == 1:
            outcome_message = "奴隷側の勝利！🎊"
        elif player_result == -1:
            outcome_message = "皇帝側の勝利！💀"

    st.session_state.round_result_message = f"あなたは **{player_card}**、AIは **{ai_card}** を出しました。{outcome_message}"
    st.session_state.current_round += 1

    if st.session_state.current_round >= MAX_ROUNDS:
        st.session_state.game_started = False # ゲーム終了
        
    st.rerun() # UIを更新


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
            st.session_state.current_round = 0
            st.session_state.player_score = 0
            st.session_state.ai_score = 0
            st.rerun()
    with col_slave:
        if st.button("奴隷側を選ぶ⛓️", use_container_width=True):
            st.session_state.player_side = "奴隷側"
            st.session_state.ai_side = "皇帝側"
            st.session_state.player_hand = HANDS["奴隷側"].copy()
            st.session_state.ai_hand = HANDS["皇帝側"].copy()
            st.session_state.game_started = True
            st.session_state.current_round = 0
            st.session_state.player_score = 0
            st.session_state.ai_score = 0
            st.rerun()
else: # ゲーム進行中
    st.header(f"--- 第 {st.session_state.current_round + 1} 回戦 ---")
    st.subheader(f"あなたの役割: {st.session_state.player_side}")

    # スコア表示
    st.markdown(f"**スコア**: あなた ({st.session_state.player_side}): {st.session_state.player_score} vs AI ({st.session_state.ai_side}): {st.session_state.ai_score}")

    # 手札表示
    st.subheader("あなたの手札:")
    st.write(get_hand_display(st.session_state.player_hand))

    # AIの手札表示 (デバッグ用またはヒントとして)
    # st.sidebar.subheader("AIの手札 (デバッグ用):")
    # st.sidebar.write(get_hand_display(st.session_state.ai_hand))

    # 直前の対戦結果
    if st.session_state.round_result_message:
        st.info(st.session_state.round_result_message)
        if st.session_state.last_player_card and st.session_state.last_ai_card:
             st.write(f"前回のあなたの手: {st.session_state.last_player_card}, 前回のAIの手: {st.session_state.last_ai_card}")

    if st.session_state.current_round < MAX_ROUNDS:
        st.subheader("カードを選択してください:")
        
        cols = st.columns(len(st.session_state.player_hand))
        
        available_cards_to_play = [card for card, count in st.session_state.player_hand.items() if count > 0]
        
        for i, card in enumerate([EMPEROR, CITIZEN, SLAVE]): # 表示順序を固定
            if card in available_cards_to_play:
                with cols[i]:
                    if st.button(f"出す: {card}", key=f"play_{card}"):
                        play_round(card)
            else:
                with cols[i]:
                    st.button(f"出す: {card}", key=f"play_{card}_disabled", disabled=True)

    else: # ゲーム終了
        st.header("--- ゲーム終了！ ---")
        if st.session_state.player_score > st.session_state.ai_score:
            st.balloons()
            st.success(f"🥳 あなた ({st.session_state.player_side}) の勝利です！ {st.session_state.player_score} 対 {st.session_state.ai_score} 🥳")
        elif st.session_state.player_score < st.session_state.ai_score:
            st.error(f"残念... AI ({st.session_state.ai_side}) の勝利です。 {st.session_state.player_score} 対 {st.session_state.ai_score} 💀")
            st.image("https://media.tenor.com/images/30b91e92c286d9c614b80a373b526685/tenor.gif", caption="ざわ…ざわ…", width=200) # カイジ感出すためのGIF
        else:
            st.warning(f"引き分けです！ {st.session_state.player_score} 対 {st.session_state.ai_score} 🤝")

        st.button("もう一度プレイする", on_click=reset_game, type="primary")

st.markdown("---")
st.markdown("© 2024 カイジ Eカードアプリ (Inspired by Kaiji Ultimate Survivor)")
