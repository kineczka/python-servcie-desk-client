from ui_main import ServiceDeskApp


if __name__ == "__main__":
    app = ServiceDeskApp()
    app.load_users()
    app.load_tickets()
    app.mainloop()