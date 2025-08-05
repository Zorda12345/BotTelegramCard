import time
from token import * #Importamos el token
import telebot #manejar Api de telegram (consultar pyTelegramBotApi)
import threading
TOKEN_TELEGRAM = "8247777433:AAGLIlTGV6FwqrPEWhMuVimr3g2fI-jHIiQ"
MI_CHAT_ID = 1326048001
CANAL_CARTAS = -4905992224

#instancioamos el bot
bot = telebot.TeleBot(TOKEN_TELEGRAM)

#responde al comando /start (esto es un decorador)
#Esto es basicamente lo que escribimos en el chat para que el bot nos responda con el /
@bot.message_handler(commands=["start" , "ayuda" , "help"]) 

def cmd_start(message):
    #Da la bienvenida al usuario del bot
    bot.reply_to(message,"Hola!, ¿Listos Para las Cartitas?")
    print(message.chat.id)#print para que muestre el chat id con el que este hablando

#Con el content types solo responde a los mensajes de texto que no son comandos
@bot.message_handler(content_types=["text"]) #Dentro de eso entra una foto,video, imagen...
def bot_mensajes_texto(message):
    #Gestiona los mensajes de texto recibidos
    if message.text.startswith("/"): #Esto es para que si ponemos /loquesea no nos diga el 2º mensaje
        bot.send_message(message.chat.id,"Comando no Disponible")
    else:
        x = bot.send_message(message.chat.id,"Escribe mejor los comandos para poder entendernos")
        time.sleep(3)#Dejamos un tiempo para que el chat le de teiempo a leer
        #bot.delete_message(message.chat.id,x.message_id) #Esto es si queremos borrar el mensaje x
        #Ponemos el identificador del chat, y el identificador del mensaje
        #Pero si queremos tmb borrar el mensaje que ha puesto nuestro usuario:
        #bot.delete_message(message.chat.id,message.message_id) 
        
    #chat_id es referente al id especidfico con el que hablamos exclusivamente


#<b></b> negrita
#<i></i> cursiva
#<u></u> subrayado
#<a></a> enlace
#<code></code> monoespaciado




def recibir_mensajes():
    bot.infinity_polling() #Bucle infinito que compruba el mensaje del usuario
    

#===============================
#           MAIN
#=================================
if __name__ == '__main__':
    bot.set_my_commands([ #Esto hace que cuando pongas una / en el chat aparezca una descripcion de lo que hace cada comando
        telebot.types.BotCommand("/start","da la bienvenida"), 
        telebot.types.BotCommand("/ayuda","da la bienvenida"),
        telebot.types.BotCommand("/help","da la bienvenida"),
        
        ])
    print('iniciando bot')
    #Ahora lo que queremos es ejecutar el bucle infinito pero seguir añadiendo cosas
    #1º Añadimos el modulo threading
    hilo_bot = threading.Thread(name = "hilo_bot",target=recibir_mensajes)
    hilo_bot.start()
    print('Bot Iniciado')
    bot.send_message(CANAL_CARTAS,"Hola jefe")
        
