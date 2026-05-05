SERVER_IP = "172.20.10.10" #ip serwera
SERVER_PORT = "8181"

USER_WSDL = f"https://{SERVER_IP}:{SERVER_PORT}/user-service/UserWebServiceImplService?wsdl"
TICKET_WSDL = f"https://{SERVER_IP}:{SERVER_PORT}/ticket-service/TicketWebServiceImplService?wsdl"
ATTACHMENT_WSDL = f"https://{SERVER_IP}:{SERVER_PORT}/attachment-service/AttachmentWebServiceImplService?wsdl"

APP_TITLE = "Service Desk Python Client"
WINDOW_SIZE = "1250x760"