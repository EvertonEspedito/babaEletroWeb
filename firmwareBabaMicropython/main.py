
# ============================================================
# BABA ELETRONICA IOT
# Raspberry Pi Pico W + MicroPython
# Comunicacao HTTP com backend Django
# ============================================================

from machine import Pin, ADC, PWM
import network
import time
import ujson

try:
    import urequests
except ImportError:
    import requests as urequests

# ---------------- CONFIGURACAO ----------------

WIFI_SSID = "NOME_DA_SUA_REDE"
WIFI_PASSWORD = "SENHA_DA_SUA_REDE"

# URL do Django acessivel pela internet.
# Exemplo: https://seu-projeto.example.com
SERVER_URL = "DOMINIO_DO_SEU_BACKEND_DJANGO"

# Deve ser igual a chave cadastrada no Django.
DEVICE_KEY = "26b4de845ab8448caf9a6501143e7598bf6c1b24a762c67c041b0be9e6bc7235"

# Ajuste conforme os testes do microfone.
SOUND_THRESHOLD = 5000
DETECTIONS_REQUIRED = 3

HEARTBEAT_INTERVAL = 15000
ALERT_COOLDOWN = 15000
ALARM_DURATION = 10000

# ------------------------------------------------

# Sensor analogico de som
microfone = ADC(28)

# Buzzer
buzzer = PWM(Pin(21))
buzzer.freq(2000)
buzzer.duty_u16(0)

# Botoes ligados entre GPIO e GND
botao_mudo = Pin(5, Pin.IN, Pin.PULL_UP)
botao_teste = Pin(6, Pin.IN, Pin.PULL_UP)

# LED RGB
led_r = Pin(13, Pin.OUT)
led_g = Pin(11, Pin.OUT)
led_b = Pin(12, Pin.OUT)

# OLED opcional
try:
    from machine import I2C
    import ssd1306

    i2c = I2C(
        1,
        sda=Pin(14),
        scl=Pin(15),
        freq=400000
    )

    oled = ssd1306.SSD1306_I2C(128, 64, i2c)

except Exception:
    oled = None
    print("OLED indisponivel; continuando sem display.")

# Wi-Fi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

# Estado do sistema
muted = False
alarm_active = False
alarm_until = 0

high_count = 0
last_level = 0

last_alert = time.ticks_add(
    time.ticks_ms(), -ALERT_COOLDOWN
)

last_heartbeat = time.ticks_add(
    time.ticks_ms(), -HEARTBEAT_INTERVAL
)

last_display = 0


# ---------------- HARDWARE ----------------

def set_led(red, green, blue):
    led_r.value(red)
    led_g.value(green)
    led_b.value(blue)


def alarm_start():
    global alarm_active, alarm_until

    alarm_active = True
    alarm_until = time.ticks_add(
        time.ticks_ms(), ALARM_DURATION
    )

    set_led(1, 0, 0)

    if not muted:
        buzzer.duty_u16(32768)


def alarm_stop():
    global alarm_active

    alarm_active = False
    buzzer.duty_u16(0)
    set_led(0, 1, 0)


# ---------------- WIFI ----------------

def connect_wifi():
    if wifi.isconnected():
        return True

    print("Conectando ao Wi-Fi...")

    try:
        wifi.connect(WIFI_SSID, WIFI_PASSWORD)

        start = time.ticks_ms()

        while not wifi.isconnected():
            elapsed = time.ticks_diff(
                time.ticks_ms(), start
            )

            if elapsed >= 10000:
                print("Falha na conexao Wi-Fi.")
                return False

            time.sleep_ms(250)

        print("Wi-Fi conectado:", wifi.ifconfig()[0])
        return True

    except Exception as error:
        print("Erro Wi-Fi:", error)
        return False


# ---------------- COMUNICACAO DJANGO ----------------

def send_to_django(endpoint, data):
    if not connect_wifi():
        return False

    response = None

    try:
        url = SERVER_URL.rstrip("/") + endpoint

        headers = {
            "Content-Type": "application/json",
            "X-Device-Key": DEVICE_KEY
        }

        response = urequests.post(
            url,
            data=ujson.dumps(data),
            headers=headers
        )

        success = (
            response.status_code >= 200
            and response.status_code < 300
        )

        if success:
            print("Dados enviados:", endpoint)
        else:
            print(
                "Erro HTTP:",
                response.status_code,
                endpoint
            )

        return success

    except Exception as error:
        print("Falha no envio:", error)
        return False

    finally:
        if response is not None:
            try:
                response.close()
            except Exception:
                pass


def send_heartbeat():
    data = {
        "device": "pico-w-baba-eletronica",
        "online": True,
        "sound_level": last_level
    }

    return send_to_django(
        "/iot/heartbeat/",
        data
    )


def send_alert(level):
    data = {
        "type": "possible_cry",
        "message": "Som elevado detectado. Verifique o bebe.",
        "sound_level": level
    }

    return send_to_django(
        "/iot/alert/",
        data
    )


# ---------------- OLED ----------------

def update_display():
    if oled is None:
        return

    try:
        oled.fill(0)

        oled.text("BABA ELETRONICA", 0, 0)
        oled.text("Som: {}".format(last_level), 0, 16)

        oled.text(
            "WiFi: {}".format(
                "OK" if wifi.isconnected() else "OFF"
            ),
            0,
            28
        )

        if muted:
            alarm_status = "MUDO"
        elif alarm_active:
            alarm_status = "ATIVO"
        else:
            alarm_status = "DESLIGADO"

        oled.text("Alarme: " + alarm_status, 0, 40)
        oled.text("GP5 Mudo GP6 Teste", 0, 54)

        oled.show()

    except Exception as error:
        print("Erro OLED:", error)


# ---------------- INICIALIZACAO ----------------

print("================================")
print("BABA ELETRONICA IOT")
print("Inicializando dispositivo...")
print("================================")

connect_wifi()


# ---------------- LOOP PRINCIPAL ----------------

while True:
    now = time.ticks_ms()

    # Botao de mudo
    if botao_mudo.value() == 0:
        muted = not muted

        if muted:
            buzzer.duty_u16(0)
        elif alarm_active:
            buzzer.duty_u16(32768)

        print("Mudo:", muted)
        time.sleep_ms(250)

    # Botao de teste
    if botao_teste.value() == 0:
        alarm_start()
        print("Teste manual do alarme")
        time.sleep_ms(250)

    # Leitura do microfone analogico
    raw = microfone.read_u16()

    # Estimativa simples de amplitude sonora
    level = abs(raw - 32768)
    last_level = level

    if level >= SOUND_THRESHOLD:
        high_count += 1
    else:
        high_count = 0

    # Deteccao de som elevado com intervalo entre alertas
    if (
        high_count >= DETECTIONS_REQUIRED
        and time.ticks_diff(now, last_alert) >= ALERT_COOLDOWN
    ):
        alarm_start()

        print("Som elevado:", level)
        send_alert(level)

        last_alert = time.ticks_ms()
        high_count = 0

    # Desligamento do alarme
    if (
        alarm_active
        and time.ticks_diff(now, alarm_until) >= 0
    ):
        alarm_stop()

    elif alarm_active:
        if muted:
            buzzer.duty_u16(0)
        else:
            buzzer.duty_u16(32768)

    # Envio periodico do estado do dispositivo
    if time.ticks_diff(now, last_heartbeat) >= HEARTBEAT_INTERVAL:
        send_heartbeat()
        last_heartbeat = time.ticks_ms()

    # Atualizacao do display
    if time.ticks_diff(now, last_display) >= 500:
        update_display()
        last_display = now

    time.sleep_ms(50)
