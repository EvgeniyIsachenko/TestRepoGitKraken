import secrets
import string
import pyperclip
import threading
import time
import os

def generate_custom_password():
    forbidden = set('#"\'\\/|}[{~`')
    special_chars = "".join(c for c in string.punctuation if c not in forbidden)
    
    # Прямая генерация без лишних списков
    letters_up = [secrets.choice(string.ascii_uppercase) for _ in range(4)]
    letters_low = [secrets.choice(string.ascii_lowercase) for _ in range(4)]
    digits = [secrets.choice(string.digits.replace('0', '')) for _ in range(8)]
    symbols = [secrets.choice(special_chars) for _ in range(6)]
    
    pool = letters_up + letters_low + digits
    secrets.SystemRandom().shuffle(pool)
    
    # Края
    prefix, suffix = pool.pop(), pool.pop()
    
    # Середина
    middle = pool + symbols
    secrets.SystemRandom().shuffle(middle)
    
    return f"{prefix}{''.join(middle)}{suffix}"

def clear_clipboard_timer(delay, password_to_clear):
    time.sleep(delay)
    try:
        if pyperclip.paste() == password_to_clear:
            pyperclip.copy("")
            # Используем \r для обновления строки без создания новой
            print("\r[!] Буфер очищен.               ", end="", flush=True)
    except: pass

def main():
    CLEANUP_DELAY = 20
    COUNT = 10
    
    while True:
        # Очистка экрана консоли (Mac/Linux)
        os.system('clear') 
        print(f"\n🔒 Генератор паролей (v2026) | Таймер: {CLEANUP_DELAY}с 🔒")
        passwords = [generate_custom_password() for _ in range(COUNT)]

        for i, pwd in enumerate(passwords, 1):
            print(f"{i:2d}. {pwd}")

        print("\n[R] - Обновить список | [Enter] - Выход")
        
        while True:
            choice = input(f"Выбор (1-{COUNT}): ").strip().lower()
            
            if not choice: return
            if choice == 'r': break # Выход во внешний цикл для регенерации
            
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= COUNT:
                    selected = passwords[idx - 1]
                    pyperclip.copy(selected)
                    
                    print(f"✓ {idx} скопирован в буфер!")
                    
                    threading.Thread(
                        target=clear_clipboard_timer, 
                        args=(CLEANUP_DELAY, selected), 
                        daemon=True
                    ).start()
                    continue
            
            print(f"Ошибка! Введите 1-{COUNT} или 'R'")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nВыход...")
