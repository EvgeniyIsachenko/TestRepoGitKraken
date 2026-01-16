import secrets, string, threading, os, sys

try:
    import pyperclip
except ImportError:
    print("\033[91m[!] Ошибка: pip install pyperclip\033[0m")
    sys.exit(1)

class Colors:
    GREEN, YELLOW, RED, CYAN = '\033[92m', '\033[93m', '\033[91m', '\033[96m'
    BOLD, END = '\033[1m', '\033[0m'

class SecureGenerator:
    def __init__(self, count=10, delay=20, pwd_length=24):
        self.count, self.delay, self.pwd_length = count, delay, pwd_length
        self.passwords_ba, self.last_timer = [], None
        self.forbidden = set('#"\'\\/|}[{~`lI1O0')
        self.specials = set(string.punctuation) # Вынесено из функции
        
        self.chars = {
            'up': [c for c in string.ascii_uppercase if c not in self.forbidden],
            'low': [c for c in string.ascii_lowercase if c not in self.forbidden],
            'dig': [c for c in string.digits if c not in self.forbidden],
            'sp': [c for c in string.punctuation if c not in self.forbidden]
        }
        self.all_allowed = [c for s in self.chars.values() for c in s]
        self.cryptogen = secrets.SystemRandom() # Один экземпляр для всех задач

    def secure_zero(self):
        for ba in self.passwords_ba:
            for i in range(len(ba)): ba[i] = 0
        self.passwords_ba.clear()

    def generate_one(self):
        pwd = [secrets.choice(self.chars[k]) for k in self.chars]
        pwd += [secrets.choice(self.all_allowed) for _ in range(self.pwd_length - 4)]
        self.cryptogen.shuffle(pwd) # Использование кешированного генератора

        for i in [0, -1]:
            if pwd[i] in self.specials:
                for j in range(1, len(pwd)-1):
                    if pwd[j] not in self.specials:
                        pwd[i], pwd[j] = pwd[j], pwd[i]
                        break
        return bytearray("".join(pwd), 'ascii')

    def clear_clipboard(self, p_str):
        try:
            if pyperclip.paste() == p_str:
                pyperclip.copy("")
                # Упрощенная очистка без лишних сохранений позиции
                sys.stdout.write(f"\r\033[K{Colors.RED}[!] Буфер очищен{Colors.END}\n{Colors.CYAN}>>> {Colors.END}")
                sys.stdout.flush()
        except: pass

    def exit_gracefully(self):
        if sys.platform == 'darwin':
            os.system('echo "" | pbcopy')
            try:
                import termios
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
            except: pass
        self.secure_zero()
        os._exit(0)

    def run(self):
        while True:
            self.secure_zero()
            self.passwords_ba = [self.generate_one() for _ in range(self.count)]
            os.system('clear' if os.name == 'posix' else 'cls')
            print(f"{Colors.BOLD}{Colors.CYAN}🔒 Secure Gen 2026 | Длина: {self.pwd_length} 🔒{Colors.END}")

            for i, ba in enumerate(self.passwords_ba, 1):
                print(f"{Colors.GREEN}{i:2d}.{Colors.END} {ba.decode('ascii')}")

            print(f"\n{Colors.YELLOW}[R]{Colors.END} Обновить | {Colors.YELLOW}[Enter]{Colors.END} Выход")

            while True:
                try:
                    cmd = input(f"{Colors.CYAN}>>> {Colors.END}").strip().lower()
                except: self.exit_gracefully()

                if not cmd: self.exit_gracefully()
                if cmd == 'r': break

                if cmd.isdigit() and 1 <= int(cmd) <= self.count:
                    idx = int(cmd)
                    p_str = self.passwords_ba[idx - 1].decode('ascii')
                    if self.last_timer: self.last_timer.cancel()
                    pyperclip.copy(p_str)
                    sys.stdout.write(f"\033[1A\033[K{Colors.GREEN}✓ #{idx} в буфере{Colors.END}\n")
                    self.last_timer = threading.Timer(self.delay, self.clear_clipboard, [p_str])
                    self.last_timer.start()
                else:
                    sys.stdout.write(f"{Colors.RED}Ошибка!{Colors.END}\n")

if __name__ == "__main__":
    SecureGenerator().run()
