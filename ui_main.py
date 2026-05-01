from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Optional

from config import APP_TITLE, WINDOW_SIZE
from soap_client import UserSoapClient, TicketSoapClient, AttachmentSoapClient
from ui_dialogs import UserFormDialog, TicketFormDialog, TicketDetailsDialog


def _safe_str(value: Any) -> str:
    return "" if value is None else str(value)


def _result_success(result: Any) -> bool:
    return bool(getattr(result, "success", False))


def _result_message(result: Any) -> str:
    return _safe_str(getattr(result, "message", "Brak komunikatu"))


class ServiceDeskApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)

        self.user_client = UserSoapClient()
        self.ticket_client = TicketSoapClient()
        self.attachment_client = AttachmentSoapClient()

        self._build_ui()

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.users_frame = ttk.Frame(notebook)
        self.tickets_frame = ttk.Frame(notebook)

        notebook.add(self.users_frame, text="Użytkownicy")
        notebook.add(self.tickets_frame, text="Zgłoszenia")

        self._build_users_tab()
        self._build_tickets_tab()

    def _build_users_tab(self) -> None:
        toolbar = ttk.Frame(self.users_frame)
        toolbar.pack(fill="x", padx=10, pady=10)

        ttk.Button(toolbar, text="Odśwież", command=self.load_users).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Dodaj", command=self.add_user).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Edytuj", command=self.edit_user).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Usuń", command=self.delete_user).pack(side="left", padx=4)

        columns = ("id", "firstName", "lastName", "email", "phone", "role")
        self.users_tree = ttk.Treeview(self.users_frame, columns=columns, show="headings", height=22)

        headings = {
            "id": "ID",
            "firstName": "Imię",
            "lastName": "Nazwisko",
            "email": "Email",
            "phone": "Telefon",
            "role": "Rola",
        }

        for col in columns:
            self.users_tree.heading(col, text=headings[col])
            self.users_tree.column(col, width=150, anchor="w")

        self.users_tree.column("id", width=80, anchor="center")
        self.users_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _build_tickets_tab(self) -> None:
        toolbar = ttk.Frame(self.tickets_frame)
        toolbar.pack(fill="x", padx=10, pady=10)

        ttk.Button(toolbar, text="Odśwież", command=self.load_tickets).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Dodaj", command=self.add_ticket).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Edytuj", command=self.edit_ticket).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Usuń", command=self.delete_ticket).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Szczegóły", command=self.show_ticket_details).pack(side="left", padx=4)

        ttk.Label(toolbar, text="Status:").pack(side="left", padx=(20, 4))
        self.ticket_status_filter = tk.StringVar(value="ALL")
        ttk.Combobox(
            toolbar,
            textvariable=self.ticket_status_filter,
            values=["ALL", "NEW", "IN_PROGRESS", "RESOLVED", "CLOSED"],
            state="readonly",
            width=18,
        ).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Filtruj", command=self.load_tickets).pack(side="left", padx=4)

        columns = ("id", "title", "status", "priority", "reporterName", "location", "createdAt")
        self.tickets_tree = ttk.Treeview(self.tickets_frame, columns=columns, show="headings", height=22)

        headings = {
            "id": "ID",
            "title": "Tytuł",
            "status": "Status",
            "priority": "Priorytet",
            "reporterName": "Zgłaszający",
            "location": "Lokalizacja",
            "createdAt": "Utworzono",
        }

        for col in columns:
            self.tickets_tree.heading(col, text=headings[col])
            self.tickets_tree.column(col, width=150, anchor="w")

        self.tickets_tree.column("id", width=80, anchor="center")
        self.tickets_tree.column("title", width=250)
        self.tickets_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _selected_tree_id(self, tree: ttk.Treeview) -> Optional[int]:
        selection = tree.selection()
        if not selection:
            return None
        values = tree.item(selection[0], "values")
        if not values:
            return None
        return int(values[0])

    def load_users(self) -> None:
        try:
            users = self.user_client.get_all_users()
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)

            for user in users:
                self.users_tree.insert(
                    "",
                    "end",
                    values=(
                        _safe_str(getattr(user, "id", None)),
                        _safe_str(getattr(user, "firstName", None)),
                        _safe_str(getattr(user, "lastName", None)),
                        _safe_str(getattr(user, "email", None)),
                        _safe_str(getattr(user, "phone", None)),
                        _safe_str(getattr(user, "role", None)),
                    ),
                )
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się pobrać użytkowników.\n\n{exc}")

    def add_user(self) -> None:
        def submit(payload: dict) -> Any:
            return self.user_client.add_user(payload)

        UserFormDialog(self, "Nowy użytkownik", submit, on_success=self.load_users)

    def edit_user(self) -> None:
        user_id = self._selected_tree_id(self.users_tree)
        if user_id is None:
            messagebox.showwarning("Brak wyboru", "Zaznacz użytkownika.")
            return

        try:
            user = self.user_client.get_user_by_id(user_id)
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się pobrać użytkownika.\n\n{exc}")
            return

        def submit(payload: dict) -> Any:
            return self.user_client.update_user(payload)

        UserFormDialog(self, "Edycja użytkownika", submit, initial_data=user, on_success=self.load_users)

    def delete_user(self) -> None:
        user_id = self._selected_tree_id(self.users_tree)
        if user_id is None:
            messagebox.showwarning("Brak wyboru", "Zaznacz użytkownika.")
            return

        if not messagebox.askyesno("Potwierdzenie", "Usunąć zaznaczonego użytkownika?"):
            return

        try:
            result = self.user_client.delete_user(user_id)
            if _result_success(result):
                messagebox.showinfo("Sukces", _result_message(result))
                self.load_users()
            else:
                messagebox.showerror("Błąd", _result_message(result))
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się usunąć użytkownika.\n\n{exc}")

    def load_tickets(self) -> None:
        try:
            status = self.ticket_status_filter.get()
            tickets = (
                self.ticket_client.get_all_tickets()
                if status == "ALL"
                else self.ticket_client.get_tickets_by_status(status)
            )

            for item in self.tickets_tree.get_children():
                self.tickets_tree.delete(item)

            for ticket in tickets:
                self.tickets_tree.insert(
                    "",
                    "end",
                    values=(
                        _safe_str(getattr(ticket, "id", None)),
                        _safe_str(getattr(ticket, "title", None)),
                        _safe_str(getattr(ticket, "status", None)),
                        _safe_str(getattr(ticket, "priority", None)),
                        _safe_str(getattr(ticket, "reporterName", None)),
                        _safe_str(getattr(ticket, "location", None)),
                        _safe_str(getattr(ticket, "createdAt", None)),
                    ),
                )
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się pobrać zgłoszeń.\n\n{exc}")

    def add_ticket(self) -> None:
        try:
            users = self.user_client.get_all_users()
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się pobrać użytkowników.\n\n{exc}")
            return

        if not users:
            messagebox.showwarning("Brak użytkowników", "Najpierw dodaj co najmniej jednego użytkownika.")
            return

        def submit(payload: dict) -> Any:
            return self.ticket_client.add_ticket(payload)

        TicketFormDialog(self, "Nowe zgłoszenie", users, submit, on_success=self.load_tickets)

    def edit_ticket(self) -> None:
        ticket_id = self._selected_tree_id(self.tickets_tree)
        if ticket_id is None:
            messagebox.showwarning("Brak wyboru", "Zaznacz zgłoszenie.")
            return

        try:
            ticket = self.ticket_client.get_ticket_by_id(ticket_id)
            users = self.user_client.get_all_users()
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się pobrać danych zgłoszenia.\n\n{exc}")
            return

        def submit(payload: dict) -> Any:
            return self.ticket_client.update_ticket(payload)

        TicketFormDialog(self, "Edycja zgłoszenia", users, submit, initial_data=ticket, on_success=self.load_tickets)

    def delete_ticket(self) -> None:
        ticket_id = self._selected_tree_id(self.tickets_tree)
        if ticket_id is None:
            messagebox.showwarning("Brak wyboru", "Zaznacz zgłoszenie.")
            return

        if not messagebox.askyesno("Potwierdzenie", "Usunąć zaznaczone zgłoszenie?"):
            return

        try:
            result = self.ticket_client.delete_ticket(ticket_id)
            if _result_success(result):
                messagebox.showinfo("Sukces", _result_message(result))
                self.load_tickets()
            else:
                messagebox.showerror("Błąd", _result_message(result))
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się usunąć zgłoszenia.\n\n{exc}")

    def show_ticket_details(self) -> None:
        ticket_id = self._selected_tree_id(self.tickets_tree)
        if ticket_id is None:
            messagebox.showwarning("Brak wyboru", "Zaznacz zgłoszenie.")
            return

        TicketDetailsDialog(
            self,
            ticket_id=ticket_id,
            ticket_client=self.ticket_client,
            attachment_client=self.attachment_client,
            on_refresh_tickets=self.load_tickets,
        )