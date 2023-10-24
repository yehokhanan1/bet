import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import random

def value_of_hand(hand):
    """Calcula o valor de uma mão de blackjack."""
    val = 0
    aces = 0
    for card in hand:
        if card in ['J', 'Q', 'K']:
            val += 10
        elif card == 'A':
            val += 11
            aces += 1
        else:
            val += int(card)
    while val > 21 and aces:
        val -= 10
        aces -= 1
    return val

count = 0  # Contagem de cartas inicial
played_cards = {}

def blackjack_decision(player_hand, dealer_card):
    global count, played_cards
    print(count)
    print(played_cards)

    def is_soft_hand(hand):
        return 'A' in hand and sum([card_value(card) for card in hand]) + 10 <= 21

    def card_value(card):
        if card in ['J', 'Q', 'K']:
            return 10
        elif card == 'A':
            return 1
        else:
            return int(card)

    def value_of_hand(hand):
        return sum([card_value(card) for card in hand])

    # Sistema de contagem Hi-Lo
    card_count_values = {
        '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
        '7': 0, '8': 0, '9': 0,
        '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
    }
    count += card_count_values.get(dealer_card, 0)
    for card in player_hand:
        count += card_count_values.get(card, 0)
    print(count)
    # Estimar o número de baralhos restantes
    total_cards_played = len(played_cards)
    decks_remaining = max(1, (8 * 52 - total_cards_played) / 52)
    true_count = count / decks_remaining
    print(true_count)
    print(decks_remaining)
    value = value_of_hand(player_hand)
    soft = is_soft_hand(player_hand)
    cards_num = len(player_hand)
    
    def card_probability(card):
        card_count = played_cards.get(card, 0)
        return (8 * 4 - card_count) / (52 * 8 - total_cards_played)


    def success_probability(action):
        if action == "Dobrar":
            if value == 10:
                return sum(card_probability(card) for card in ['10', 'J', 'Q', 'K', 'A'])
            elif value == 9:
                return sum(card_probability(card) for card in ['2', '3', '4', '5', '6'])
            else:
                return sum(card_probability(str(i)) for i in range(1, 12-value+1))
        elif action == "Pedir":
            return sum(card_probability(str(i)) for i in range(1, 22-value+1))
        elif action == "Dividir":
            # Estimativa simplificada
            return 0.5
        else:
            return None

    action = "Pedir"  # Ação padrão

    # Se o jogador tem um par
    if cards_num == 2 and player_hand[0] == player_hand[1]:
        if player_hand[0] in ['8', 'A']:
            return "Dividir"
        elif player_hand[0] in ['2', '3', '7'] and dealer_card in ['2', '3', '4', '5', '6', '7']:
            return "Dividir"
        elif player_hand[0] == '6' and dealer_card in ['2', '3', '4', '5', '6']:
            return "Dividir"
        elif player_hand[0] == '4' and dealer_card in ['5', '6']:
            return "Dividir"
        elif player_hand[0] == '10' and count >= 4:  # Dividir 10s quando a contagem é alta
            return "Dividir"

    # Para totais suaves
    if soft:
        if cards_num == 2 and value + 10 == 17 and dealer_card in [3, 4, 5, 6]:
            return "Dobrar"
        
    # Estratégia básica para decidir quando "Parar"
    if value >= 17:
        return "Parar"
    elif value >= 13 and dealer_card in ['2', '3', '4', '5', '6']:
        return "Parar"
    
    # Estratégias avançadas usando a contagem verdadeira (true count)
    if cards_num == 2 and value <= 11 and true_count > 1:
        return "Dobrar"
    if true_count > 2 and value == 10 and dealer_card not in ['10', 'J', 'Q', 'K', 'A']:
        return "Dobrar"
    if true_count < -2 and value >= 16:
        return "Pedir"
    if true_count < -4:
        return "Cash Out"

    # Estratégia de contagem de cartas para decidir quando "Parar"
    if value == 16 and true_count >= 0:  # Pedir com 16 se a contagem for favorável
        return "Pedir"
    elif value == 15 and true_count > 1:  # Pedir com 15 se a contagem for muito favorável
        return "Pedir"

    prob = success_probability(action)
    if prob is not None:
        return f"{action} P: {prob:.2%}"
    else:
        return action

def get_input(title, prompt):
    """Função auxiliar para pegar entrada do usuário via interface gráfica."""
    return simpledialog.askstring(title, prompt)

deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4 * 8  # 13 cartas x 4 naipes x 8 baralhos

def renew_deck():
    global deck, played_cards
    deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4 * 8
    played_cards.clear()
    
def draw_card():
    global deck
    if len(deck) == 0:
        renew_deck()
    card = random.choice(deck)
    deck.remove(card)
    played_cards.add(card)
    return card

def main_gui():
    window = tk.Tk()
    window.title("Blackjack Helper")

    # Load the background image
    pil_image = Image.open("background.png")
    bg_image = ImageTk.PhotoImage(pil_image)

    # Set the window size based on the image dimensions
    window.geometry(f"{bg_image.width()}x{bg_image.height()}")

    canvas = tk.Canvas(window, width=bg_image.width(), height=bg_image.height())
    canvas.pack(fill="both", expand=True)

    # Set the background image
    canvas.create_image(0, 0, image=bg_image, anchor="nw")

    # Ask which player you are (from 1 to 7)
    my_player_index = int(simpledialog.askstring("Qual Jogador Você É?", "Indique o número do jogador (de 1 a 7) que você é:")) - 1

    # Variables for all players including yourself
    player_vars = [tk.StringVar() for _ in range(7)]
    decision_vars = [tk.StringVar() for _ in range(7)]

    # Variables for the dealer
    dealer_card_var = tk.StringVar()

    def process():
        # Get dealer's card
        dealer_card = dealer_card_var.get().upper()

        # Process each player's hand
        for idx, player_var in enumerate(player_vars):
            hand = player_var.get().upper().split()
            decision = blackjack_decision(hand, dealer_card)
            decision_vars[idx].set(f"D: {decision}")

    def finalize_round():
        # Recuperando a carta "virada" do dealer
        facedown_card = dealer_card_var.get().upper()

        dealer_final_hand = simpledialog.askstring("Final do Dealer", "Insira as cartas finais do dealer (separadas por espaço):").upper().split()
        
        # Adicionando a carta "virada" do dealer à lista das cartas finais do dealer
        dealer_final_hand.append(facedown_card)

        for card in dealer_final_hand:
            if card in deck:
                deck.remove(card)
            played_cards[card] = played_cards.get(card, 0) + 1

        # Removing player cards from the deck
        for idx, player_var in enumerate(player_vars):
            hand = player_var.get().upper().split()
            for card in hand:
                if card in deck:
                    deck.remove(card)
                played_cards[card] = played_cards.get(card, 0) + 1
            player_vars[idx].set('')

        # Clear dealer's card entry
        dealer_card_var.set('')

    def check_deck():
        if len(deck) < 52:
            messagebox.showinfo("Info", f"Restam {len(deck)} cartas no baralho.")
    
    def reset_deck():
        deck.clear()
        deck.extend(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4 * 8)

    # Criar e posicionar a label e a entrada para a carta do dealer no Canvas
    dealer_label = tk.Label(window, text="Carta do Dealer:")
    canvas.create_window(440, 300, window=dealer_label)

    dealer_entry = tk.Entry(window, textvariable=dealer_card_var)
    canvas.create_window(550, 300, window=dealer_entry)

    # Criar e posicionar as entradas e labels para as mãos dos jogadores no Canvas
    # Y posição central dos retângulos
    y_center = bg_image.height() * 0.65  # Ajuste esse valor conforme necessário

    # X posições para as entradas e labels dos jogadores
    spacing_between_entries = bg_image.width() / 8  # Dividindo por 8 para ter 7 espaços entre 8 posições

    for i, (player_var, decision_var) in enumerate(zip(player_vars, decision_vars)):
        # Ajuste a posição x para começar da direita para a esquerda
        x_position = bg_image.width() - ((i + 1) * spacing_between_entries)
        
        label_text = "Sua Mão:" if i == my_player_index else f"Jogador {i + 1}:"
        player_label = tk.Label(window, text=label_text)
        canvas.create_window(x_position, y_center - 20, window=player_label)  # 20 pixels acima do centro

        player_entry = tk.Entry(window, textvariable=player_var)
        canvas.create_window(x_position, y_center + 20, window=player_entry)  # 20 pixels abaixo do centro

        decision_label = tk.Label(window, textvariable=decision_var)
        canvas.create_window(x_position, y_center + 60, window=decision_label)  # 60 pixels abaixo do centro

    # Criar e posicionar os botões no Canvas
    # Valores para espaçamento
    spacing = 10
    button_width = 90  # Aproximado

    # X posições para os botões
    x1 = (bg_image.width() / 2) - (3 * button_width) - (2.5 * spacing)
    x2 = (bg_image.width() / 2) - (1.5 * button_width) - (1.5 * spacing)
    x3 = (bg_image.width() / 2) + (0.5 * button_width) - (0.5 * spacing)
    x4 = (bg_image.width() / 2) + (2.5 * button_width) + (0.5 * spacing)

    # Y posição para todos os botões
    y_buttons = bg_image.height() - 80  # 50 pixels a partir da parte inferior da imagem

    calc_button = tk.Button(window, text="Calcular Decisão", command=process)
    canvas.create_window(x1, y_buttons, window=calc_button)

    final_button = tk.Button(window, text="Finalizar Rodada", command=finalize_round)
    canvas.create_window(x2, y_buttons, window=final_button)

    check_button = tk.Button(window, text="Verificar Baralho", command=check_deck)
    canvas.create_window(x3, y_buttons, window=check_button)

    reset_button = tk.Button(window, text="Renovar Baralho", command=reset_deck)
    canvas.create_window(x4, y_buttons, window=reset_button)
    # Ensure your main loop and other parts remain intact
    window.mainloop()

if __name__ == "__main__":
    main_gui()
