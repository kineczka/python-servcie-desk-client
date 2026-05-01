SERVER_IP = "192.168.1.23" #ip serwera
SERVER_PORT = "8080"

USER_WSDL = f"http://{SERVER_IP}:{SERVER_PORT}/user-service/UserWebServiceImplService?wsdl"
TICKET_WSDL = f"http://{SERVER_IP}:{SERVER_PORT}/ticket-service/TicketWebServiceImplService?wsdl"
ATTACHMENT_WSDL = f"http://{SERVER_IP}:{SERVER_PORT}/attachment-service/AttachmentWebServiceImplService?wsdl"

APP_TITLE = "Service Desk Python Client"
WINDOW_SIZE = "1250x760"