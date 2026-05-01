from __future__ import annotations

from typing import Any, List
from requests import Session
from zeep import Client, Settings
from zeep.transports import Transport

from config import USER_WSDL, TICKET_WSDL, ATTACHMENT_WSDL


def _build_client(wsdl_url: str) -> Client:
    session = Session()
    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    return Client(wsdl=wsdl_url, transport=transport, settings=settings)


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    try:
        return list(value)
    except TypeError:
        return [value]


class UserSoapClient:
    def __init__(self) -> None:
        self.client = _build_client(USER_WSDL)
        self.service = self.client.service

    def get_all_users(self) -> List[Any]:
        return _as_list(self.service.getAllUsers())

    def get_user_by_id(self, user_id: int) -> Any:
        return self.service.getUserById(user_id)

    def add_user(self, payload: dict) -> Any:
        return self.service.addUser(payload)

    def update_user(self, payload: dict) -> Any:
        return self.service.updateUser(payload)

    def delete_user(self, user_id: int) -> Any:
        return self.service.deleteUser(user_id)


class TicketSoapClient:
    def __init__(self) -> None:
        self.client = _build_client(TICKET_WSDL)
        self.service = self.client.service

    def get_all_tickets(self) -> List[Any]:
        return _as_list(self.service.getAllTickets())

    def get_ticket_by_id(self, ticket_id: int) -> Any:
        return self.service.getTicketById(ticket_id)

    def get_tickets_by_status(self, status: str) -> List[Any]:
        return _as_list(self.service.getTicketsByStatus(status))

    def add_ticket(self, payload: dict) -> Any:
        return self.service.addTicket(payload)

    def update_ticket(self, payload: dict) -> Any:
        return self.service.updateTicket(payload)

    def delete_ticket(self, ticket_id: int) -> Any:
        return self.service.deleteTicket(ticket_id)

    def change_status(self, payload: dict) -> Any:
        return self.service.changeStatus(payload)


class AttachmentSoapClient:
    def __init__(self) -> None:
        self.client = _build_client(ATTACHMENT_WSDL)
        self.service = self.client.service

    def get_attachments_by_ticket_id(self, ticket_id: int) -> List[Any]:
        return _as_list(self.service.getAttachmentsByTicketId(ticket_id))

    def upload_attachment(self, ticket_id: int, file_name: str, content_type: str, data: bytes) -> Any:
        return self.service.uploadAttachment(ticket_id, file_name, content_type, data)

    def download_attachment(self, attachment_id: int) -> Any:
        return self.service.downloadAttachment(attachment_id)

    def delete_attachment(self, attachment_id: int) -> Any:
        return self.service.deleteAttachment(attachment_id)