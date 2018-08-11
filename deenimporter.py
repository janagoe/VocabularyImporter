from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *

from DeEnImporter.parse.input_parser import InputParser
from DeEnImporter.anki_inserter import AnkiInserter
from DeEnImporter.ui.input_dialog import InputDialog
from DeEnImporter.ui.progress_bar import ProgressBar
from DeEnImporter.get_model import get_model
from DeEnImporter.parse.example_parser import ExampleParser
from DeEnImporter.parse.translation_parser import TranslationParser
from DeEnImporter.download.media_loader import MediaLoader


##############################################################################

def run():
    data = InputDialog().run()
    if not data:
        return

    text, translations_nr, sentences_nr, images_nr, audios_nr,\
        from_lang, dest_lang, from_audio_wanted, dest_audio_wanted = data

    vocabs = InputParser().read_input(text)

    progress_bar = ProgressBar(len(vocabs))
    # progress_bar.run()

    # setup anki collection for insertions
    #################################################

    deck_name = "VocabImporter"

    # select deck
    deck_id = mw.col.decks.id(deck_name, create=True)
    mw.col.decks.select(deck_id)
    deck = mw.col.decks.current()

    # select model
    model = get_model(mw.col)
    model['did'] = deck_id

    deck['mid'] = model['id']
    mw.col.decks.save(deck)
    mw.col.models.save()

    #################################################

    # parsing downloads and inserting
    translation_parser = TranslationParser(from_lang, dest_lang, translations_nr)
    example_parser = ExampleParser(from_lang, dest_lang, sentences_nr)
    media_loader = MediaLoader(from_lang, dest_lang, from_audio_wanted, dest_audio_wanted, images_nr, audios_nr)
    inserter = AnkiInserter(mw.col, model, from_lang, dest_lang)

    for vocab in vocabs:
        translation = translation_parser.parse(vocab)
        if translation:
            sentences = example_parser.parse(vocab)
            images, audios = media_loader.load(vocab)

            inserter.insert(translation, sentences, images, audios)

        progress_bar.finished_action()

    # saving and clearing everything up
    inserter.save()
    finish_message(inserter.get_count())


def finish_message(count):
    count *= 2
    if count > 0:
        showInfo("Successfully created %d new cards." % count)
    else:
        showInfo("No cards could be created.")


# setup anki gui
##############################################################################

importAction = QAction("Import Input", mw)
importAction.triggered.connect(run)
mw.form.menuTools.addAction(importAction)

