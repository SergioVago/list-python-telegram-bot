from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram.ext import MessageHandler, Filters
import os

PORT = int(os.environ.get('PORT', 5000))

TOKEN = os.environ['TOKEN']

NAME_LIST, JOIN_LIST, CHANGE_NAME = range(3)

isOpen = False
nomeLista = ""

adminList = [675141232]


def ehAdmin(user):
    for admin in adminList:
        if(user.id == admin):
            return True

    return False


def start(update, context):
    user = update.message.from_user

    if(ehAdmin(user)):
        message = "Digite /cancel para cancelar \nDefina o nome da lista: \n"

        if(isOpen):
            message = "Lista: " + nomeLista + " aberta. Digite um novo nome para apagar essa lista e criar uma nova ou /cancel para cancelar"

        update.message.reply_text(message)

        return NAME_LIST

    update.message.reply_text(
        'Sem permissão', reply_markup = ReplyKeyboardRemove())

    return ConversationHandler.END


def join(update, context):
    if(isOpen == False):
        update.message.reply_text(text = "Lista fechada")
        return ConversationHandler.END

    user=update.message.from_user
    user.insta=update.message.text
    for userList in usersList:
        if(userList.id == user.id):
            update.message.reply_text(
                text = "Você já está na lista " + nomeLista + ". Digite seu instagram (sem o @) para alterar o seu instagram na lista (Digite /cancel para cancelar a troca de nome)")
            return CHANGE_NAME

    update.message.reply_text(
        "Digite /cancel para cancelar \n" +
        "Digite seu instagram (sem o @) para entrar na lista: \n")

    return JOIN_LIST


def joinList(update, context):
    user=update.message.from_user
    user.insta=update.message.text

    usersList.append(user)
    update.message.reply_text(
        text = user.insta + " entrou na lista " + nomeLista)

    return ConversationHandler.END


def changeName(update, context):
    user=update.message.from_user
    user.insta=update.message.text

    for userList in usersList:
        if(userList.id == user.id):
            userList.insta=user.insta

    update.message.reply_text(
        text = user.username + " alterou o próprio nome na lista para " + user.insta)
    return ConversationHandler.END


def setNameList(update, context):
    user=update.message.from_user

    if(ehAdmin(user)):
        global isOpen
        isOpen=True

        global usersList
        usersList=[]

        global nomeLista
        nomeLista=update.message.text

        update.message.reply_text('Lista criada com o nome: ' + nomeLista)

        return ConversationHandler.END

    update.message.reply_text(
        'Sem permissão', reply_markup = ReplyKeyboardRemove())

    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text(
        'Cancelado', reply_markup = ReplyKeyboardRemove())

    return ConversationHandler.END


def stop(update, context):
    user=update.message.from_user

    if(ehAdmin(user)):
        global isOpen

        message="Nenhuma lista aberta"
        if(isOpen):
            message="Lista " + nomeLista + " fechada"

        isOpen=False
        update.message.reply_text(message)

        return ConversationHandler.END


    update.message.reply_text(
        'Sem permissão', reply_markup = ReplyKeyboardRemove())

    return ConversationHandler.END


def echo(update, context):
    context.bot.send_message(
        chat_id = update.effective_chat.id, text = update.message.text)


def formatLista():
    if(nomeLista == ""):
        return "Nenhuma lista disponível"

    texto="" + nomeLista + ": \n"
    cont=0

    for user in usersList:
        cont += 1
        texto += "" + str(cont) + ". " + "@" + user.insta + "\n"

    return texto


def getLista(update, context):
    update.message.reply_text(
        formatLista()
    )


def getId(update, context):
    user=update.message.from_user
    print(user)
    update.message.reply_text(user.id)


def iamAdmin(update, context):
    user=update.message.from_user
    message="Não"
    if(ehAdmin(user)):
        message="Sim"

    update.message.reply_text(message)


def main():
    updater=Updater(TOKEN, use_context = True)

    dp=updater.dispatcher

    conv_handler=ConversationHandler(
        entry_points = [
            CommandHandler('start', start),
            CommandHandler('join', join),
        ],

        states = {
            NAME_LIST: [MessageHandler(
                Filters.text & (~Filters.command), setNameList)],
            JOIN_LIST: [MessageHandler(
                Filters.text & (~Filters.command), joinList)],
            CHANGE_NAME: [MessageHandler(
                Filters.text & (~Filters.command), changeName)],
        },

        fallbacks = [CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('list', getLista))
    dp.add_handler(CommandHandler('getId', getId))
    dp.add_handler(CommandHandler('iamAdmin', iamAdmin))
    dp.add_handler(CommandHandler('stop', stop))

    # dp.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

    if(os.environ.get('ENV') == "DEV"):
        updater.start_polling()

    else:
        updater.start_webhook(listen = "0.0.0.0",
                                port = int(PORT),
                                url_path = TOKEN)

        updater.bot.setWebhook(
            'https://list-python-telegram-bot.herokuapp.com/' + TOKEN)

    updater.idle()

if __name__ == "__main__":
    main()
