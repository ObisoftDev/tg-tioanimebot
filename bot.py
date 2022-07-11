from telegram import ChatAction,InlineQueryResultArticle,InlineQueryResultPhoto, ParseMode, InputTextMessageContent, Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext,MessageHandler,Filters
from telegram.utils.helpers import escape_markdown
from uuid import uuid4
import TioAnime
import os

def inlinequery(update: Update, context: CallbackContext) -> None:
    try:
        query = update.inline_query.query

        directorySize = TioAnime.getDirectorySize()

        if query == "":
            results = []
            episodies = TioAnime.extractUltimosEpisodios()
            index = 0
            for cap in episodies:
                results.append(InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=cap['Anime'],
                    thumb_url=cap['Image'],
                    input_message_content=InputTextMessageContent('/capitulo '+str(index))
                ))
                index+=1
            update.inline_query.answer(results)
        else:
            results = []
            index = 0
            try:
                index = int(query)
                animes = TioAnime.searchDirectory(index)
                ii = 0
                for anime in animes:
                    results.append(InlineQueryResultArticle(
                        id=str(uuid4()),
                        title=anime['Anime'],
                        thumb_url=anime['Image'],
                        input_message_content=InputTextMessageContent('/anime ' + str(index) + ' ' + str(ii),parse_mode=ParseMode.HTML)
                    ))
                    ii+=1
            except Exception as ex:
                results.append(InlineQueryResultArticle(
                        id=str(uuid4()),
                        title= '❌' + query + ' no es un directorio valido 1-' + str(directorySize) + '❌',
                        input_message_content=InputTextMessageContent('<a href="https://tioanime.com/directorio"><b>#tioanime</b></a>',parse_mode=ParseMode.HTML)
                    ))
            update.inline_query.answer(results,cache_time=0)
    except Exception as ex:
        print(str(ex))


def sendHtml(update,html):
    update.message.reply_text(html, parse_mode=ParseMode.HTML)

def process_msg(update,context):
    msg = update.message.text

    if '/start' in msg:
        reply = '<a href="https://tioanime.com/assets/img/logo-ft.png">~<b>Bienvenidos Al Bot De TioAnime</b>~</a>\n'
        reply += '<b>Actualizaciones:</b>\n'
        reply += '<b>1-Buscador En Linea "Ultimos Episodios"</b>\n'
        reply += '<b>2-Buscador En Linea "Directorio" 1-'+str(TioAnime.getDirectorySize())+'</b>\n'
        reply += '<b>3-Exrtaccion de Enlace de Descarga</b>\n'
        reply += '<b>4-Soporte Para Series Completas</b>\n'
        sendHtml(update,reply)

    if '/capitulo ' in msg:
        index = int(str(msg).replace('/capitulo ',''))
        update.message.chat.send_action(action=ChatAction.UPLOAD_DOCUMENT)
        capitulos = TioAnime.extractUltimosEpisodios()
        episodio = capitulos[index]
        megaurl = TioAnime.getMegaUrl(episodio['Url'])
        html = '<a href="'+episodio['Image']+'">'+episodio['Anime']+'</a>'
        update.message.reply_text(html,parse_mode=ParseMode.HTML,reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='Mega Url',url=megaurl)]
            ]))

    if '/anime ' in msg:
        indexs = str(msg).replace('/anime ','').split(' ')
        update.message.chat.send_action(action=ChatAction.UPLOAD_DOCUMENT)
        animes = TioAnime.searchDirectory(int(indexs[0]))
        anime = animes[int(indexs[1])]
        caps = TioAnime.getAnimeEpisodies(anime['Url'])
        html = '<a href="'+anime['Image']+'">'+anime['Anime']+'</a>\n'
        html+= '<b>Sinopsis:</b>\n' + caps['sinopsis'] + '\n\n'
        html+= '<b>Capitulos:</b>' + str(len(caps['episodies']))
        buttons = []
        index = 1
        for cap in caps['episodies']:
            try:
                mega = TioAnime.getMegaUrl(cap)
                buttons.append([InlineKeyboardButton(text='Capitulo '+str(index)+' Mega Url',url=mega)])
            except Exception as ex:
                pass
            index+=1
        update.message.reply_text(html,parse_mode=ParseMode.HTML,reply_markup=InlineKeyboardMarkup(buttons))
        pass

    pass

def main() -> None:
    try:
        bot_token = os.environ.get('bot_token')
        updater = Updater(bot_token)

        dispatcher = updater.dispatcher

        dispatcher.add_handler(MessageHandler(Filters.text,process_msg))
        dispatcher.add_handler(InlineQueryHandler(inlinequery,pass_update_queue=True))

        updater.start_polling()
        updater.idle()
    except Exception as ex:
        print(str(ex))
        main()


if __name__ == '__main__':
    main()
