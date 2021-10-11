from repository.DatabaseRepository import DatabaseRepository
from controller.Controller import Controller
from ui.MusicPlayerGUI import GUI


repository = DatabaseRepository()
controller = Controller(repository)
start_app = GUI(controller, repository)

start_app.start()

start_app.close_connection()
