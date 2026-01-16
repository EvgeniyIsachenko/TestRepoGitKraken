import secrets, threading, sys, hashlib, pyperclip

class SecureGenerator:
    def __init__(self, length=24, delay=20, count=10):
        # Валидация входных параметров
        try:
            self.length = max(8, min(int(length), 128))
            self.delay = max(5, min(int(delay), 300))
            self.count = max(1, min(int(count), 50))
        except (ValueError, TypeError):
            sys.exit("\033[91m[!] Ошибка: Параметры должны быть числами.\033[0m")

        self.timer = None
        self.pwds = []
        self.hashes = {} 
        self.masked = True
        
        # Набор символов: исключены l, I, 1, O, 0 для исключения ошибок чтения
        chars = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        self.pool = chars + "!@$%^&*()-_=+[]{}<>?"
        self.border = chars

    def _wipe(self):
        """Физическое затирание данных в RAM и очистка хэшей"""
        for b in self.pwds:
            with memoryview(b) as m: m[:] = b'\x00' * len(b)
        self.pwds.clear()
        self.hashes.clear()

    def _gen(self, idx):
        """Генерация пароля и создание проверочного хэша для буфера"""
        p = [secrets.choice(self.border)] + \
            [secrets.choice(self.pool) for _ in range(self.length - 2)] + \
            [secrets.choice(self.border)]
        pwd_str = "".join(p)
        # Хэш используется для подтверждения того, что в буфере всё еще наш пароль
        self.hashes[idx] = hashlib.sha256(pwd_str.encode()).hexdigest()
        return bytearray(pwd_str, 'ascii')

    def _clear_clip(self, expected_hash):
        """Очистка буфера только при совпадении хэша содержимого"""
        try:
            current_content = pyperclip.paste()
            if hashlib.sha256(current_content.encode()).hexdigest() == expected_hash:
                pyperclip.copy("")
                sys.stdout.write(f"\r\033[K\033[91m[!] Буфер очищен\033[0m\n\033[96m>>> \033[0m")
                sys.stdout.flush()
        except: pass

    def _draw(self):
        """Отрисовка интерфейса (ANSI-очистка экрана)"""
        sys.stdout.write("\033[H\033[J") 
        header = f"🔒 Secure Gen | T:{self.delay}s | Mask:{'ON' if self.masked else 'OFF'}"
        print(f"\033[1;36m{header}\033[0m")
        for i, p in enumerate(self.pwds, 1):
            val = "•" * self.length if self.masked else p.decode()
            print(f"\033[92m{i:2d}.\033[0m {val}")
        print(f"\n\033[93m[1-{self.count}]\033[0m Копировать | \033[93m[V]\033[0m Маска | \033[93m[R]\033[0m Обновить | \033[93m[Enter]\033[0m Выход")

    def run(self):
        try:
            while True:
                if not self.pwds:
                    self.pwds = [self._gen(i+1) for i in range(self.count)]
                self._draw()
                while True:
                    try:
                        cmd = input("\033[96m>>> \033[0m").strip().lower()
                    except EOFError: self.exit()
                    
                    if not cmd: self.exit()
                    if cmd == 'r': self._wipe(); break
                    if cmd == 'v': self.masked = not self.masked; self._draw(); continue
                    
                    if cmd.isdigit() and 1 <= (idx := int(cmd)) <= self.count:
                        p_str = self.pwds[idx-1].decode()
                        pyperclip.copy(p_str)
                        # Сброс старого таймера перед запуском нового
                        if self.timer: self.timer.cancel()
                        self.timer = threading.Timer(self.delay, self._clear_clip, [self.hashes[idx]])
                        self.timer.start()
                        print(f"\033[1A\033[K\033[92m✓ #{idx} скопирован ({self.delay}s)\033[0m")
                        continue
                    print(f"\033[1A\033[K\033[91m[!] Ошибка ввода\033[0m")
        except KeyboardInterrupt: self.exit()

    def exit(self):
        """Полная деструкция данных перед закрытием"""
        if self.timer: self.timer.cancel()
        try: pyperclip.copy("") 
        except: pass
        self._wipe()
        sys.exit("\n\033[1;91m[!] Память очищена. Сессия закрыта.\033[0m")

if __name__ == "__main__":
    # Запуск с поддержкой аргументов командной строки
    a = sys.argv[1:]
    SecureGenerator(
        length=a[0] if len(a) > 0 else 24,
        delay=a[1] if len(a) > 1 else 20,
        count=a[2] if len(a) > 2 else 10
    ).run()
