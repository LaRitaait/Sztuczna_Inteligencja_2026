import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

conversations = {}
buttons = {}
current_chat = None


def new_chat():
    global current_chat

    name = f"Rozmowa {len(conversations)+1}"
    conversations[name] = ""

    btn = ctk.CTkButton(
        sidebar_frame,
        text=name,
        anchor="w",
        command=lambda n=name: load_chat(n)
    )

    btn.pack(fill="x", padx=5, pady=3)

    buttons[name] = btn
    current_chat = name

    chat_box.delete("1.0", "end")


def load_chat(name):
    global current_chat

    current_chat = name

    chat_box.delete("1.0", "end")
    chat_box.insert("end", conversations[name])


def send_message():
    global current_chat

    text = entry.get()

    if not text.strip() or current_chat is None:
        return

    message = f"Ty: {text}\nAI: (tu będzie odpowiedź AI)\n\n"

    chat_box.insert("end", message)
    chat_box.see("end")

    conversations[current_chat] += message

    entry.delete(0, "end")


app = ctk.CTk()
app.geometry("900x550")
app.title("AI Assistant")

# SIDEBAR
sidebar_frame = ctk.CTkFrame(app, width=220)
sidebar_frame.pack(side="left", fill="y", padx=5, pady=5)

new_chat_button = ctk.CTkButton(
    sidebar_frame,
    text="➕ Nowa rozmowa",
    command=new_chat
)

new_chat_button.pack(padx=10, pady=10)

# CHAT
main_frame = ctk.CTkFrame(app)
main_frame.pack(side="right", fill="both", expand=True)

chat_box = ctk.CTkTextbox(main_frame)
chat_box.pack(fill="both", expand=True, padx=10, pady=10)

entry = ctk.CTkEntry(main_frame, placeholder_text="Napisz wiadomość...")
entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)

send_button = ctk.CTkButton(main_frame, text="Wyślij", command=send_message)
send_button.pack(side="right", padx=10, pady=10)

new_chat()

app.mainloop()
