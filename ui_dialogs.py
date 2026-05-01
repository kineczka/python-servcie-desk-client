from __future__ import annotations

import mimetypes
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Any, Callable, Optional


def _safe_str(value: Any) -> str:
    return "" if value is None else str(value)


def _result_success(result: Any) -> bool:
    return bool(getattr(result, "success", False))


def _result_message(result: Any) -> str:
    return _safe_str(getattr(result, "message", "Brak komunikatu"))


class UserFormDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Misc,
        title: str,
        on_submit: Callable[[dict], Any],
        initial_data: Optional[Any] = None,
        on_success: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_submit = on_submit
        self.on_success = on_success
        self.initial_data = initial_data

        self.first_name_var = tk.StringVar(value=_safe_str(getattr(initial_data, "firstName", "")))
        self.last_name_var = tk.StringVar(value=_safe_str(getattr(initial_data, "lastName", "")))
        self.email_var = tk.StringVar(value=_safe_str(getattr(initial_data, "email", "")))
        self.phone_var = tk.StringVar(value=_safe_str(getattr(initial_data, "phone", "")))
        self.role_var = tk.StringVar(value=_safe_str(getattr(initial_data, "role", "USER")) or "USER")

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=14)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Imię").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.first_name_var, width=35).grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Nazwisko").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.last_name_var, width=35).grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Email").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.email_var, width=35).grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Telefon").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.phone_var, width=35).grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Rola").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Combobox(
            frame,
            textvariable=self.role_var,
            values=["USER", "TECHNICIAN", "ADMIN"],
            state="readonly",
            width=32,
        ).grid(row=4, column=1, sticky="ew", pady=4)

        buttons = ttk.Frame(frame)
        buttons.grid(row=5, column=0, columnspan=2, sticky="e", pady=(12, 0))

        ttk.Button(buttons, text="Zapisz", command=self._save).pack(side="left", padx=4)
        ttk.Button(buttons, text="Anuluj", command=self.destroy).pack(side="left", padx=4)

    def _save(self) -> None:
        if not self.first_name_var.get().strip():
            messagebox.showwarning("Brak danych", "Podaj imię.")
            return
        if not self.last_name_var.get().strip():
            messagebox.showwarning("Brak danych", "Podaj nazwisko.")
            return
        if not self.email_var.get().strip():
            messagebox.showwarning("Brak danych", "Podaj email.")
            return

        payload = {
            "firstName": self.first_name_var.get().strip(),
            "lastName": self.last_name_var.get().strip(),
            "email": self.email_var.get().strip(),
            "phone": self.phone_var.get().strip(),
            "role": self.role_var.get().strip(),
        }

        if self.initial_data is not None and getattr(self.initial_data, "id", None) is not None:
            payload["id"] = int(self.initial_data.id)

        try:
            result = self.on_submit(payload)
            if _result_success(result):
                messagebox.showinfo("Sukces", _result_message(result))
                if self.on_success:
                    self.on_success()
                self.destroy()
            else:
                messagebox.showerror("Błąd", _result_message(result))
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się zapisać użytkownika.\n\n{exc}")


class TicketFormDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Misc,
        title: str,
        users: list[Any],
        on_submit: Callable[[dict], Any],
        initial_data: Optional[Any] = None,
        on_success: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.geometry("620x420")
        self.transient(parent)
        self.grab_set()

        self.users = users
        self.on_submit = on_submit
        self.on_success = on_success
        self.initial_data = initial_data

        self.user_label_to_id: dict[str, int] = {}
        self.id_to_user_label: dict[int, str] = {}
        for user in self.users:
            label = f"{_safe_str(getattr(user, 'firstName', ''))} {_safe_str(getattr(user, 'lastName', ''))} (ID: {_safe_str(getattr(user, 'id', ''))})"
            uid = int(getattr(user, "id"))
            self.user_label_to_id[label] = uid
            self.id_to_user_label[uid] = label

        initial_reporter_id = getattr(initial_data, "reporterId", None)
        initial_user_label = self.id_to_user_label.get(int(initial_reporter_id)) if initial_reporter_id else ""

        self.title_var = tk.StringVar(value=_safe_str(getattr(initial_data, "title", "")))
        self.location_var = tk.StringVar(value=_safe_str(getattr(initial_data, "location", "")))
        self.priority_var = tk.StringVar(value=_safe_str(getattr(initial_data, "priority", "MEDIUM")) or "MEDIUM")
        self.user_var = tk.StringVar(value=initial_user_label)

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self, padding=14)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Tytuł").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.title_var, width=50).grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Opis").grid(row=1, column=0, sticky="nw", pady=4)
        self.description_text = tk.Text(frame, width=50, height=8)
        self.description_text.grid(row=1, column=1, sticky="ew", pady=4)
        if self.initial_data is not None:
            self.description_text.insert("1.0", _safe_str(getattr(self.initial_data, "description", "")))

        ttk.Label(frame, text="Lokalizacja").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.location_var, width=50).grid(row=2, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Priorytet").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Combobox(
            frame,
            textvariable=self.priority_var,
            values=["LOW", "MEDIUM", "HIGH"],
            state="readonly",
            width=47,
        ).grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Zgłaszający").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Combobox(
            frame,
            textvariable=self.user_var,
            values=list(self.user_label_to_id.keys()),
            state="readonly",
            width=47,
        ).grid(row=4, column=1, sticky="ew", pady=4)

        buttons = ttk.Frame(frame)
        buttons.grid(row=5, column=0, columnspan=2, sticky="e", pady=(12, 0))

        ttk.Button(buttons, text="Zapisz", command=self._save).pack(side="left", padx=4)
        ttk.Button(buttons, text="Anuluj", command=self.destroy).pack(side="left", padx=4)

        frame.columnconfigure(1, weight=1)

    def _save(self) -> None:
        title = self.title_var.get().strip()
        description = self.description_text.get("1.0", "end").strip()
        location = self.location_var.get().strip()
        priority = self.priority_var.get().strip()
        user_label = self.user_var.get().strip()

        if not title:
            messagebox.showwarning("Brak danych", "Podaj tytuł.")
            return
        if not user_label:
            messagebox.showwarning("Brak danych", "Wybierz zgłaszającego.")
            return

        reporter_id = self.user_label_to_id[user_label]
        reporter_name = user_label.split(" (ID:")[0]

        payload = {
            "title": title,
            "description": description,
            "location": location,
            "priority": priority,
            "reporterId": reporter_id,
            "reporterName": reporter_name,
        }

        if self.initial_data is not None:
            payload["id"] = int(getattr(self.initial_data, "id"))
            payload["status"] = _safe_str(getattr(self.initial_data, "status", "NEW"))
            payload["createdAt"] = getattr(self.initial_data, "createdAt", None)
            payload["updatedAt"] = getattr(self.initial_data, "updatedAt", None)

        try:
            result = self.on_submit(payload)
            if _result_success(result):
                messagebox.showinfo("Sukces", _result_message(result))
                if self.on_success:
                    self.on_success()
                self.destroy()
            else:
                messagebox.showerror("Błąd", _result_message(result))
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się zapisać zgłoszenia.\n\n{exc}")


class TicketDetailsDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Misc,
        ticket_id: int,
        ticket_client: Any,
        attachment_client: Any,
        on_refresh_tickets: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(parent)
        self.title(f"Szczegóły zgłoszenia #{ticket_id}")
        self.geometry("900x650")
        self.transient(parent)
        self.grab_set()

        self.ticket_id = ticket_id
        self.ticket_client = ticket_client
        self.attachment_client = attachment_client
        self.on_refresh_tickets = on_refresh_tickets

        self.ticket = None
        self.attachments = []

        self.status_var = tk.StringVar()

        self._build_ui()
        self.load_data()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill="both", expand=True)

        self.details_text = tk.Text(outer, height=10, state="disabled")
        self.details_text.pack(fill="x", pady=(0, 10))

        status_frame = ttk.LabelFrame(outer, text="Zmiana statusu")
        status_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(status_frame, text="Nowy status:").pack(side="left", padx=8, pady=8)
        ttk.Combobox(
            status_frame,
            textvariable=self.status_var,
            values=["NEW", "IN_PROGRESS", "RESOLVED", "CLOSED"],
            state="readonly",
            width=20,
        ).pack(side="left", padx=8, pady=8)

        ttk.Button(status_frame, text="Zmień status", command=self.change_status).pack(side="left", padx=8, pady=8)

        upload_frame = ttk.LabelFrame(outer, text="Załączniki")
        upload_frame.pack(fill="both", expand=True)

        top_buttons = ttk.Frame(upload_frame)
        top_buttons.pack(fill="x", pady=(8, 8))

        ttk.Button(top_buttons, text="Odśwież załączniki", command=self.load_attachments).pack(side="left", padx=4)
        ttk.Button(top_buttons, text="Dodaj zdjęcie / plik", command=self.upload_attachment).pack(side="left", padx=4)
        ttk.Button(top_buttons, text="Pobierz zaznaczony", command=self.download_attachment).pack(side="left", padx=4)
        ttk.Button(top_buttons, text="Usuń zaznaczony", command=self.delete_attachment).pack(side="left", padx=4)

        columns = ("id", "fileName", "contentType", "uploadedAt")
        self.attachments_tree = ttk.Treeview(upload_frame, columns=columns, show="headings", height=14)

        self.attachments_tree.heading("id", text="ID")
        self.attachments_tree.heading("fileName", text="Nazwa pliku")
        self.attachments_tree.heading("contentType", text="Typ")
        self.attachments_tree.heading("uploadedAt", text="Wysłano")

        self.attachments_tree.column("id", width=80, anchor="center")
        self.attachments_tree.column("fileName", width=300)
        self.attachments_tree.column("contentType", width=180)
        self.attachments_tree.column("uploadedAt", width=180)

        self.attachments_tree.pack(fill="both", expand=True, pady=(0, 8))

    def load_data(self) -> None:
        try:
            self.ticket = self.ticket_client.get_ticket_by_id(self.ticket_id)
            self._render_ticket()
            self.load_attachments()
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się pobrać szczegółów zgłoszenia.\n\n{exc}")

    def _render_ticket(self) -> None:
        if self.ticket is None:
            return

        self.status_var.set(_safe_str(getattr(self.ticket, "status", "NEW")))

        lines = [
            f"ID: {_safe_str(getattr(self.ticket, 'id', None))}",
            f"Tytuł: {_safe_str(getattr(self.ticket, 'title', None))}",
            f"Opis: {_safe_str(getattr(self.ticket, 'description', None))}",
            f"Status: {_safe_str(getattr(self.ticket, 'status', None))}",
            f"Priorytet: {_safe_str(getattr(self.ticket, 'priority', None))}",
            f"Lokalizacja: {_safe_str(getattr(self.ticket, 'location', None))}",
            f"Zgłaszający: {_safe_str(getattr(self.ticket, 'reporterName', None))}",
            f"Utworzono: {_safe_str(getattr(self.ticket, 'createdAt', None))}",
            f"Zaktualizowano: {_safe_str(getattr(self.ticket, 'updatedAt', None))}",
        ]

        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", "\n".join(lines))
        self.details_text.configure(state="disabled")

    def load_attachments(self) -> None:
        try:
            self.attachments = self.attachment_client.get_attachments_by_ticket_id(self.ticket_id)
            for item in self.attachments_tree.get_children():
                self.attachments_tree.delete(item)

            for attachment in self.attachments:
                self.attachments_tree.insert(
                    "",
                    "end",
                    values=(
                        _safe_str(getattr(attachment, "id", None)),
                        _safe_str(getattr(attachment, "fileName", None)),
                        _safe_str(getattr(attachment, "contentType", None)),
                        _safe_str(getattr(attachment, "uploadedAt", None)),
                    ),
                )
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się pobrać załączników.\n\n{exc}")

    def change_status(self) -> None:
        try:
            payload = {
                "ticketId": self.ticket_id,
                "newStatus": self.status_var.get(),
            }
            result = self.ticket_client.change_status(payload)
            if _result_success(result):
                messagebox.showinfo("Sukces", _result_message(result))
                self.load_data()
                if self.on_refresh_tickets:
                    self.on_refresh_tickets()
            else:
                messagebox.showerror("Błąd", _result_message(result))
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się zmienić statusu.\n\n{exc}")

    def upload_attachment(self) -> None:
        file_path = filedialog.askopenfilename(title="Wybierz plik")
        if not file_path:
            return

        try:
            with open(file_path, "rb") as file:
                data = file.read()

            import os
            file_name = os.path.basename(file_path)
            content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

            result = self.attachment_client.upload_attachment(
                self.ticket_id,
                file_name,
                content_type,
                data,
            )

            if _result_success(result):
                messagebox.showinfo("Sukces", _result_message(result))
                self.load_attachments()
            else:
                messagebox.showerror("Błąd", _result_message(result))
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się wysłać pliku.\n\n{exc}")

    def _selected_attachment_id(self) -> Optional[int]:
        selection = self.attachments_tree.selection()
        if not selection:
            return None
        values = self.attachments_tree.item(selection[0], "values")
        if not values:
            return None
        return int(values[0])

    def download_attachment(self) -> None:
        attachment_id = self._selected_attachment_id()
        if attachment_id is None:
            messagebox.showwarning("Brak wyboru", "Zaznacz załącznik.")
            return

        try:
            file_data = self.attachment_client.download_attachment(attachment_id)
            if file_data is None:
                messagebox.showerror("Błąd", "Nie udało się pobrać pliku.")
                return

            file_name = _safe_str(getattr(file_data, "fileName", "plik.bin"))
            data = getattr(file_data, "data", None)

            if data is None:
                messagebox.showerror("Błąd", "Brak danych pliku.")
                return

            save_path = filedialog.asksaveasfilename(
                title="Zapisz plik",
                initialfile=file_name,
            )
            if not save_path:
                return

            with open(save_path, "wb") as file:
                file.write(data)

            messagebox.showinfo("Sukces", "Plik został zapisany.")
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się pobrać pliku.\n\n{exc}")

    def delete_attachment(self) -> None:
        attachment_id = self._selected_attachment_id()
        if attachment_id is None:
            messagebox.showwarning("Brak wyboru", "Zaznacz załącznik.")
            return

        if not messagebox.askyesno("Potwierdzenie", "Usunąć zaznaczony załącznik?"):
            return

        try:
            result = self.attachment_client.delete_attachment(attachment_id)
            if _result_success(result):
                messagebox.showinfo("Sukces", _result_message(result))
                self.load_attachments()
            else:
                messagebox.showerror("Błąd", _result_message(result))
        except Exception as exc:
            messagebox.showerror("Błąd", f"Nie udało się usunąć załącznika.\n\n{exc}")