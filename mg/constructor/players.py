from mg import *
from uuid import uuid4
from mg.constructor.interface_classes import *
from mg.game.money_classes import *
import re

re_delete_recover = re.compile(r'^(delete|recover)/(\S+)$')
re_combo_value = re.compile(r'\s*(\S+)\s*:\s*(.*?)\s*$')

# Database objects

class DBPlayer(CassandraObject):
    _indexes = {
        "created": [[], "created"],
    }

    def __init__(self, *args, **kwargs):
        kwargs["clsprefix"] = "Player-"
        CassandraObject.__init__(self, *args, **kwargs)

    def indexes(self):
        return DBPlayer._indexes

class DBPlayerList(CassandraObjectList):
    def __init__(self, *args, **kwargs):
        kwargs["clsprefix"] = "Player-"
        kwargs["cls"] = DBPlayer
        CassandraObjectList.__init__(self, *args, **kwargs)

class DBCharacter(CassandraObject):
    _indexes = {
        "created": [[], "created"],
        "player": [["player"], "created"],
        "admin": [["admin"]]
    }

    def __init__(self, *args, **kwargs):
        kwargs["clsprefix"] = "Character-"
        CassandraObject.__init__(self, *args, **kwargs)

    def indexes(self):
        return DBCharacter._indexes

class DBCharacterList(CassandraObjectList):
    def __init__(self, *args, **kwargs):
        kwargs["clsprefix"] = "Character-"
        kwargs["cls"] = DBCharacter
        CassandraObjectList.__init__(self, *args, **kwargs)

class DBCharacterForm(CassandraObject):
    _indexes = {
    }

    def __init__(self, *args, **kwargs):
        kwargs["clsprefix"] = "CharacterForm-"
        CassandraObject.__init__(self, *args, **kwargs)

    def indexes(self):
        return DBCharacterForm._indexes

class DBCharacterFormList(CassandraObjectList):
    def __init__(self, *args, **kwargs):
        kwargs["clsprefix"] = "CharacterForm-"
        kwargs["cls"] = DBCharacterForm
        CassandraObjectList.__init__(self, *args, **kwargs)

class DBCharacterOnline(CassandraObject):
    _indexes = {
        "all": [[]]
    }

    def __init__(self, *args, **kwargs):
        kwargs["clsprefix"] = "CharacterOnline-"
        CassandraObject.__init__(self, *args, **kwargs)

    def indexes(self):
        return DBCharacterOnline._indexes

class DBCharacterOnlineList(CassandraObjectList):
    def __init__(self, *args, **kwargs):
        kwargs["clsprefix"] = "CharacterOnline-"
        kwargs["cls"] = DBCharacterOnline
        CassandraObjectList.__init__(self, *args, **kwargs)

# Business logic objects

class Character(Module):
    def __init__(self, app, uuid, fqn="mg.constructor.players.Character"):
        Module.__init__(self, app, fqn)
        self.uuid = uuid

    @property
    def db_character(self):
        try:
            return self._db_character
        except AttributeError:
            self._db_character = self.obj(DBCharacter, self.uuid)
            return self._db_character

    @property
    def db_user(self):
        try:
            return self._db_user
        except AttributeError:
            self._db_user = self.obj(User, self.uuid)
            return self._db_user

    @property
    def name(self):
        try:
            return self._name
        except AttributeError:
            self._name = self.db_user.get("name")
            return self._name

    @property
    def player(self):
        try:
            return self._player
        except AttributeError:
            uuid = self.db_character.get("player")
            if uuid:
                try:
                    req = self.req()
                except AttributeError:
                    return Player(self.app(), uuid)
                else:
                    try:
                        players = req.players
                    except AttributeError:
                        players = {}
                        req.players = players
                    try:
                        return players[uuid]
                    except KeyError:
                        obj = Player(self.app(), uuid)
                        players[uuid] = obj
                        return obj
            else:
                self._player = None
            return self._player

    @property
    def sex(self):
        try:
            return self._sex
        except AttributeError:
            self._sex = self.db_user.get("sex")
            return self._sex

    @property
    def html(self):
        try:
            return self._html
        except AttributeError:
            self._html = self.call("character.make-html", self, "main")
            return self._html

    @property
    def html_admin(self):
        try:
            return self._html_admin
        except AttributeError:
            self._html_admin = self.call("character.make-html", self, "admin")
            return self._html_admin

    @property
    def html_chat(self):
        try:
            return self._html_chat
        except AttributeError:
            self._html_chat = self.call("character.make-html", self, "chat")
            return self._html_chat

    @property
    def tech_online(self):
        try:
            return self._tech_online
        except AttributeError:
            try:
                self.obj(DBCharacterOnline, self.uuid)
            except ObjectNotFoundException:
                self._tech_online = False
            else:
                self._tech_online = True
            return self._tech_online

    @property
    def lock(self):
        return self.lock(["character.%s" % self.uuid])

    @property
    def roster_info(self):
        try:
            return self._roster_info
        except AttributeError:
            self._roster_info = {
                "id": self.uuid,
                "name": self.name
            }
            return self._roster_info

    @property
    def location(self):
        try:
            return self._location[0]
        except AttributeError:
            self._location = self.call("locations.character_get", self) or [None, None, None]
            return self._location[0]

    @property
    def instance(self):
        try:
            return self._location[1]
        except AttributeError:
            self._location = self.call("locations.character_get", self) or [None, None, None]
            return self._location[1]

    @property
    def location_delay(self):
        try:
            return self._location[2]
        except AttributeError:
            self._location = self.call("locations.character_get", self) or [None, None, None]
            return self._location[2]

    def set_location(self, location, instance=None, delay=None):
        old_location = self.location
        old_instance = self.instance
        self.call("locations.character_before_set", self, location, instance)
        self.call("locations.character_set", self, location, instance, delay)
        self._location = [location, instance, delay]
        self.call("locations.character_after_set", self, old_location, old_instance)

    @property
    def db_settings(self):
        try:
            return self._db_settings
        except AttributeError:
            self._db_settings = self.obj(DBCharacterSettings, self.uuid, silent=True)
            return self._db_settings

    @property
    def sessions(self):
        try:
            return self._sessions
        except AttributeError:
            self._sessions = []
            self.call("session.character-sessions", self, self._sessions)
            return self._sessions

    @property
    def money(self):
        try:
            return self._money
        except AttributeError:
            self._money = MemberMoney(self.app(), self.uuid)
            return self._money

class Player(Module):
    def __init__(self, app, uuid, fqn="mg.constructor.players.Player"):
        Module.__init__(self, app, fqn)
        self.uuid = uuid

    @property
    def db_player(self):
        try:
            return self._db_player
        except AttributeError:
            self._db_player = self.obj(DBPlayer, self.uuid)
            return self._db_player

    @property
    def valid(self):
        try:
            self.db_player
        except ObjectNotFoundException:
            return False
        else:
            return True

    @property
    def db_user(self):
        try:
            return self._db_user
        except AttributeError:
            self._db_user = self.obj(User, self.uuid)
            return self._db_user

    @property
    def email(self):
        try:
            return self._email
        except AttributeError:
            self._email = self.db_user.get("email")
            return self._email

class Characters(Module):
    def __init__(self, app, fqn="mg.constructor.players.Characters"):
        Module.__init__(self, app, fqn)

    @property
    def tech_online(self):
        try:
            return self._tech_online
        except AttributeError:
            self._tech_online = []
            self.call("auth.characters-tech-online", self._tech_online)
            return self._tech_online

# Modules

class CharactersMod(Module):
    def register(self):
        Module.register(self)
        self.rhook("menu-admin-root.index", self.menu_root_index)
        self.rhook("menu-admin-characters.index", self.menu_characters_index)
        self.rhook("ext-admin-characters.form", self.admin_characters_form, priv="players.auth")
        self.rhook("headmenu-admin-characters.form", self.headmenu_characters_form)
        self.rhook("objclasses.list", self.objclasses_list)
        self.rhook("character.make-html", self.character_make_html)
        self.rhook("dossier.record", self.dossier_record)
        self.rhook("dossier.before-display", self.dossier_before_display)
        self.rhook("dossier.after-display", self.dossier_after_display)

    def menu_root_index(self, menu):
        menu.append({"id": "characters.index", "text": self._("Characters"), "order": 20})

    def menu_characters_index(self, menu):
        req = self.req()
        if req.has_access("players.auth"):
            menu.append({"id": "characters/form", "text": self._("Character form"), "leaf": True, "order": 20})

    def admin_characters_form(self):
        req = self.req()
        character_form = self.call("character.form")
        m = re_delete_recover.match(req.args)
        if m:
            op, code = m.group(1, 2)
            for fld in character_form:
                if fld["code"] == code:
                    if op == "delete":
                        fld["deleted"] = True
                    else:
                        try:
                            del fld["deleted"]
                        except KeyError:
                            pass
                    config = self.app().config_updater()
                    config.set("auth.char_form", character_form)
                    config.store()
                    self.call("auth.char-form-changed")
                    break
            self.call("admin.redirect", "characters/form")
        if req.args:
            # Loading data
            std_values = [(0, self._("Custom field")), (1, self._("Character name")), (2, self._("Character sex"))]
            used_std_values = dict([(fld["std"], fld["code"]) for fld in character_form if fld.get("std")])
            if req.args == "new":
                show_std = True
                std = 0
                code = ""
                name = ""
                description = ""
                prompt = ""
                field_type = 0
                values = ""
                order = character_form[-1]["order"] + 10 if len(character_form) else 10
                reg = False
                mandatory_level = 0
                std_values = [val for val in std_values if not used_std_values.get(val[0])]
            else:
                ok = False
                for fld in character_form:
                    if fld["code"] == req.args:
                        std = intz(fld.get("std"))
                        code = fld.get("code")
                        name = fld.get("name")
                        field_type = intz(fld.get("type"))
                        values = fld.get("values")
                        if values:
                            values = "|".join([":".join(val) for val in values])
                        description = fld.get("description")
                        prompt = fld.get("prompt")
                        order = fld.get("order")
                        reg = fld.get("reg")
                        mandatory_level = fld.get("mandatory_level")
                        show_std = std != 1 and std != 2
                        ok = True
                        break
                if not ok:
                    self.call("admin.redirect", "characters/form")
                std_values = [val for val in std_values if not used_std_values.get(val[0]) or used_std_values[val[0]] == code]
            valid_std_values = dict([(val[0], True) for val in std_values])
            if req.ok():
                # Validating data
                if show_std:
                    std = intz(req.param("v_std"))
                name = req.param("name")
                field_type = intz(req.param("v_type"))
                values = req.param("values")
                description = req.param("description")
                prompt = req.param("prompt")
                order = floatz(req.param("order"))
                reg = req.param("reg")
                mandatory_level = req.param("mandatory_level")
                errors = {}
                if show_std and not std in valid_std_values:
                    errors["std"] = self._("Invalid selection")
                if not name:
                    errors["name"] = self._("Name may not be empty")
                if not description:
                    errors["description"] = self._("Description may not be empty")
                if not prompt:
                    errors["prompt"] = self._("Prompt may not be empty")
                if len(errors):
                    self.call("web.response_json", {"success": False, "errors": errors})
                # Storing data
                val = {
                    "name": name,
                    "description": description,
                    "prompt": prompt,
                    "order": order,
                    "std": std
                }
                if req.args == "new":
                    val["code"] = uuid4().hex
                else:
                    val["code"] = req.args
                if std == 1 or std == 2:
                    val["reg"] = True
                else:
                    val["reg"] = reg
                    if not valid_nonnegative_int(mandatory_level):
                        errors["mandatory_level"] = self._("Number expected")
                    val["mandatory_level"] = intz(mandatory_level)
                if std == 1:
                    val["type"] = 0
                elif std == 2:
                    val["type"] = 1
                else:
                    val["type"] = field_type
                if val["type"] == 1:
                    if not values:
                        errors["values"] = self._("Specify list of values")
                    else:
                        values = values.split("|")
                        val["values"] = []
                        for v in values:
                            m = re_combo_value.match(v)
                            if not m:
                                errors["values"] = self._("Invalid format")
                            vl, desc = m.group(1, 2)
                            val["values"].append([vl, desc])
                if len(errors):
                    self.call("web.response_json", {"success": False, "errors": errors})
                character_form = [fld for fld in character_form if fld["code"] != val["code"]]
                character_form.append(val)
                character_form.sort(cmp=lambda x, y: cmp(x.get("order"), y.get("order")) or cmp(x.get("name"), y.get("name")))
                config = self.app().config_updater()
                config.set("auth.char_form", character_form)
                config.store()
                self.call("auth.char-form-changed")
                self.call("admin.redirect", "characters/form")
            fields = [
                {"name": "name", "label": self._("Short description for administrators"), "value": name },
                {"name": "type", "label": self._("Form control type"), "value": field_type, "type": "combo", "values": [(0, self._("text input")), (1, self._("combo box")), (2, self._("text area"))], "condition": "![std]"},
                {"name": "values", "label": self._("Possible options. Format: 0:first value|1:second value|2:third value"), "value": values, "condition": "[type]==1 || [std]==2"},
                {"name": "order", "label": self._("Sort order"), "value": order },
                {"name": "description", "label": self._("Description for players"), "value": description },
                {"name": "prompt", "label": self._("Input prompt for players"), "value": prompt },
                {"name": "reg", "type": "checkbox", "label": self._("Show on registration"), "checked": reg, "condition": "[std]!=1 && [std]!=2"},
                {"name": "mandatory_level", "label": self._("The field is mandatory after this character level ('0' if not mandatory)"), "value": mandatory_level, "condition": "[std]!=1 && [std]!=2"},
            ]
            if show_std:
                fields.insert(0, {"name": "std", "type": "combo", "label": self._("Field type"), "value": std, "values": std_values})
            else:
                fields.insert(0, {"name": "std", "type": "hidden", "value": std})
            self.call("admin.form", fields=fields)
        self.call("admin.response_template", "admin/auth/character-form.html", {
            "fields": character_form,
            "NewField": self._("Create new field"),
            "Code": self._("Code"),
            "Name": self._("Name"),
            "Order": self._("Order"),
            "Editing": self._("Editing"),
            "Deletion": self._("Deletion"),
            "edit": self._("edit"),
            "delete": self._("delete"),
            "recover": self._("recover"),
            "Description": self._("Here you can customize parameters entered by player in the character form. These are not game parameters like strength and agility. Character form is a simple text fields like 'Legend', 'Motto' etc."),
        })

    def headmenu_characters_form(self, args):
        if args == "new":
            return [self._("New field"), "characters/form"]
        elif args:
            return [htmlescape(args), "characters/form"]
        return self._("Character form")

    def objclasses_list(self, objclasses):
        objclasses["Player"] = (DBPlayer, DBPlayerList)
        objclasses["Character"] = (DBCharacter, DBCharacterList)
        objclasses["CharacterForm"] = (DBCharacterForm, DBCharacterFormList)

    def character_make_html(self, character, mode):
        return htmlescape(character.name)

    def dossier_record(self, rec):
        try:
            char = self.obj(DBCharacter, rec.get("user"))
        except ObjectNotFoundException:
            pass
        else:
            rec.set("character", char.uuid)
            rec.set("user", char.get("player"))

    def dossier_before_display(self, dossier_info, vars):
        try:
            char = self.obj(DBCharacter, dossier_info["user"])
        except ObjectNotFoundException:
            pass
        else:
            dossier_info["user"] = char.get("player")

    def dossier_after_display(self, records, users, table):
        table["header"].append(self._("Character"))
        load_users = {}
        for rec in records:
            char_uuid = rec.get("character")
            if char_uuid and not users.get(char_uuid):
                load_users[char_uuid] = None
        if load_users:
            ulst = self.objlist(UserList, uuids=load_users.keys())
            ulst.load(silent=True)
            for ent in ulst:
                users[ent.uuid] = ent
        i = 0
        for rec in records:
            char_uuid = rec.get("character")
            user = users.get(char_uuid) if char_uuid else None
            table["rows"][i].append(u'<hook:admin.link href="auth/user-dashboard/{0}" title="{1}" />'.format(user.uuid, htmlescape(user.get("name"))) if user else None)
            i += 1
