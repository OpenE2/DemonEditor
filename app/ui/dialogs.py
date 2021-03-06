""" Common module for showing dialogs """
import locale
from enum import Enum

from app.commons import run_idle
from .uicommons import Gtk, UI_RESOURCES_PATH, TEXT_DOMAIN


class Action(Enum):
    EDIT = 0
    ADD = 1


class DialogType(Enum):
    INPUT = "input_dialog"
    CHOOSER = "path_chooser_dialog"
    ERROR = "error_dialog"
    QUESTION = "question_dialog"
    ABOUT = "about_dialog"
    WAIT = "wait_dialog"


class WaitDialog:
    def __init__(self, transient, text=None):
        builder, dialog = get_dialog_from_xml(DialogType.WAIT, transient)
        self._dialog = dialog
        self._dialog.set_transient_for(transient)
        if text is not None:
            builder.get_object("wait_dialog_label").set_text(text)

    def show(self):
        self._dialog.show()

    @run_idle
    def hide(self):
        self._dialog.hide()

    @run_idle
    def destroy(self):
        self._dialog.destroy()


def show_dialog(dialog_type: DialogType, transient, text=None, options=None, action_type=None, file_filter=None):
    """ Shows dialogs by name """
    builder, dialog = get_dialog_from_xml(dialog_type, transient)

    if dialog_type is DialogType.CHOOSER and options:
        if action_type is not None:
            dialog.set_action(action_type)
        if file_filter is not None:
            dialog.add_filter(file_filter)

        path = options.get("data_dir_path")
        dialog.set_current_folder(path)

        response = dialog.run()
        if response == -12:  # -12 for fix assertion 'gtk_widget_get_can_default (widget)' failed
            if dialog.get_filename():
                path = dialog.get_filename()
                if action_type is not Gtk.FileChooserAction.OPEN:
                    path = path + "/"

            response = path
        dialog.destroy()

        return response

    if dialog_type is DialogType.INPUT:
        entry = builder.get_object("input_entry")
        entry.set_text(text if text else "")
        response = dialog.run()
        txt = entry.get_text()
        dialog.destroy()

        return txt if response == Gtk.ResponseType.OK else Gtk.ResponseType.CANCEL

    if text:
        dialog.set_markup(get_message(text))
    response = dialog.run()
    dialog.destroy()

    return response


def get_dialog_from_xml(dialog_type, transient):
    builder = Gtk.Builder()
    builder.set_translation_domain(TEXT_DOMAIN)
    builder.add_objects_from_file(UI_RESOURCES_PATH + "dialogs.glade", (dialog_type.value,))
    dialog = builder.get_object(dialog_type.value)
    dialog.set_transient_for(transient)

    return builder, dialog


def get_chooser_dialog(transient, options, pattern, name):
    file_filter = Gtk.FileFilter()
    file_filter.add_pattern(pattern)
    file_filter.set_name(name)

    return show_dialog(dialog_type=DialogType.CHOOSER,
                       transient=transient,
                       options=options,
                       action_type=Gtk.FileChooserAction.OPEN,
                       file_filter=file_filter)


def get_message(message):
    """ returns translated message """
    return locale.dgettext(TEXT_DOMAIN, message)


if __name__ == "__main__":
    pass
