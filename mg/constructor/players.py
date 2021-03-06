#!/usr/bin/python2.6

# This file is a part of Metagam project.
#
# Metagam is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# Metagam is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Metagam.  If not, see <http://www.gnu.org/licenses/>.

from mg.constructor import *
from uuid import uuid4
from mg.constructor.player_classes import *
import re

re_delete_recover = re.compile(r'^(delete|recover)/(\S+)$')
re_combo_value = re.compile(r'\s*(\S+)\s*:\s*(.*?)\s*$')
re_tokens = re.compile(r'{([^{}]+)}')
re_valid_identifier = re.compile(r'^u_[a-z0-9_]+$', re.IGNORECASE)
re_newline = re.compile(r'\n')

class CharactersMod(ConstructorModule):
    def register(self):
        self.rhook("menu-admin-root.index", self.menu_root_index)
        self.rhook("menu-admin-characters.index", self.menu_characters_index)
        self.rhook("ext-admin-characters.form", self.admin_characters_form, priv="players.auth")
        self.rhook("headmenu-admin-characters.form", self.headmenu_characters_form)
        self.rhook("objclasses.list", self.objclasses_list)
        self.rhook("dossier.record", self.dossier_record)
        self.rhook("dossier.before-display", self.dossier_before_display)
        self.rhook("dossier.after-display", self.dossier_after_display)
        self.rhook("permissions.list", self.permissions_list)
        self.rhook("ext-admin-characters.names", self.admin_characters_names, priv="characters.names")
        self.rhook("headmenu-admin-characters.names", self.headmenu_characters_names)
        self.rhook("characters.name-purposes", self.name_purposes)
        self.rhook("characters.name-purpose-default", self.name_purpose_default)
        self.rhook("characters.name-purpose-admin", self.name_purpose_admin)
        self.rhook("characters.name-sample-params", self.name_sample_params)
        self.rhook("admin-icons.list", self.icons_list)
        self.rhook("admin-icons.changed", self.icons_changed)
        self.rhook("characters.name-params", self.name_params)
        self.rhook("characters.name-tokens", self.name_tokens)
        self.rhook("characters.name-render", self.name_render)
        self.rhook("characters.name-fixup", self.name_fixup)
        self.rhook("headmenu-admin-characters.validate-names", self.headmenu_validate_names)
        self.rhook("ext-admin-characters.validate-names", self.admin_validate_names, priv="change.usernames")
        self.rhook("ext-character.info", self.character_info, priv="public")
        self.rhook("character.info-avatar", self.character_info_avatar)
        self.rhook("character.page-avatar", self.character_page_avatar)
        self.rhook("gameinterface.buttons", self.gameinterface_buttons)
        self.rhook("ext-interface.character-form", self.interface_character_form, priv="logged")
        self.rhook("ext-interface.character", self.interface_character, priv="logged")
        self.rhook("session.character-online", self.character_online, priority=10)
        self.rhook("session.character-offline", self.character_offline, priority=10)
        self.rhook("locations.character_after_set", self.location_changed, priority=10)
        self.rhook("characters.param-changed", self.characters_param_changed, priority=10)
        self.rhook("auth.name-changed", self.name_changed, priority=10)
        self.rhook("auth.permissions-changed", self.permissions_changed, priority=10)
        self.rhook("user-modifier.created", self.modifier_created)
        self.rhook("user-modifier.destroyed", self.modifier_destroyed)
        self.rhook("user-modifier.expired", self.modifier_expired)
        self.rhook("char-inventory.changed", self.inventory_changed, priority=10)
        self.rhook("admin-gameinterface.design-files", self.design_files)
        self.rhook("character.public-info-menu", self.character_public_info_menu)
        self.rhook("characters.context-menu-available", self.context_menu_available)
        self.rhook("character.get", self.character_get)

    def context_menu_available(self, menu):
        menu.append({
            "code": "charinfo",
            "title": self._("Character info"),
            "href": ["/character/info/", [".", ["glob", "char"], "id"]],
            "order": 1.0,
            "default_visible": True,
            "image": "/st-mg/icons/character-pubinfo.png",
            "visible": 1,
        })

    def design_files(self, files):
        files.append({"filename": "character-info.html", "description": self._("Character page (external information)"), "doc": "/doc/design/character-info"})
        files.append({"filename": "character-info-avatar.html", "description": self._("Character avatar (external info)"), "doc": "/doc/design/character-info"})
        files.append({"filename": "character-page.html", "description": self._("Character page (internal)"), "doc": "/doc/design/character-page"})
        files.append({"filename": "character-page-avatar.html", "description": self._("Character avatar (internal page)"), "doc": "/doc/design/character-page"})
        files.append({"filename": "character-params.html", "description": self._("Character parameters"), "doc": "/doc/design/character-params"})

    def gameinterface_buttons(self, buttons):
        buttons.append({
            "id": "character",
            "href": "/interface/character",
            "target": "main",
            "icon": "character.png",
            "title": self._("Character"),
            "block": "left-menu",
            "order": 0,
        })
        buttons.append({
            "id": "character-form",
            "href": "/interface/character-form",
            "target": "main",
            "icon": "character-form.png",
            "title": self._("Character form"),
            "block": "left-menu",
            "order": 5,
        })

    def name_fixup(self, character, purpose, params):
        if purpose == "admin":
            params["NAME"] = u'<hook:admin.link href="auth/user-dashboard/%s" title="%s" />' % (character.uuid, htmlescape(params["NAME"]))

    def permissions_list(self, perms):
        perms.append({"id": "characters.names", "name": self._("Character names rendering editor")})

    def menu_root_index(self, menu):
        menu.append({"id": "characters.index", "text": self._("Characters"), "order": 20})

    def menu_characters_index(self, menu):
        req = self.req()
        if req.has_access("players.auth"):
            menu.append({"id": "characters/form", "text": self._("Character form"), "leaf": True, "order": 20})
        if req.has_access("characters.names"):
            menu.append({"id": "characters/names", "text": self._("Character names"), "leaf": True, "order": 25})
        if self.conf("auth.validate_names") and req.has_access("change.usernames"):
            menu.append({"id": "characters/validate-names", "text": self._("Names check"), "leaf": True, "order": 30})

    def admin_characters_form(self):
        req = self.req()
        character_form = self.call("character.form")
        self.call("admin.advice", {"title": self._("Character forms documentation"), "content": self._('How to setup character form you can read in the <a href="//www.%s/doc/character-form" target="_blank">character forms</a> manual page') % self.main_host})
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
                if req.args == "new":
                    new_code = req.param("code").strip()
                    if not new_code:
                        errors["code"] = self._("This field is mandatory")
                    elif not re_valid_identifier.match(new_code):
                        errors["code"] = self._("Identifier must start with 'u_'. Other symbols may be latin letters, digits or '_'")
                    else:
                        for fld in character_form:
                            if fld["code"] == new_code:
                                errors["code"] = self._("This code is busy")
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
                    val["code"] = new_code
                else:
                    val["code"] = req.args
                if std == 1 or std == 2:
                    val["reg"] = True
                else:
                    val["reg"] = reg
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
                            else:
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
            if req.args == "new":
                fields.insert(1, {"name": "code", "label": self._("Field code (identifier for scripting)"), "value": "u_"})
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
        objclasses["CharParams"] = (DBCharParams, DBCharParamsList)
        objclasses["CharacterSettings"] = (DBCharacterSettings, DBCharacterSettingsList)
        objclasses["CharacterBusy"] = (DBCharacterBusy, DBCharacterBusyList)

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

    def name_purposes(self, purposes):
        purposes.append(self.name_purpose_default())
        purposes.append(self.name_purpose_admin())

    def name_purpose_default(self):
        return {"id": "default", "title": self._("Default"), "order": -1000, "default": "{NAME} {INFO}"}

    def name_purpose_admin(self):
        return {"id": "admin", "title": self._("Administration interface"), "order": 0, "default": "{NAME}"}

    def icons_list(self, icons):
        icons.extend([
            {
                "code": "char-male",
                "title": self._("Male character info icon"),
            },
            {
                "code": "char-female",
                "title": self._("Female character info icon"),
            },
        ])

    def icons_changed(self):
        self.app().mc.incr_ver("character-names")

    def name_params(self, characters, params):
        for char in characters:
            ent = params[char.uuid]
            ent["NAME"] = u'<span class="char-name">%s</span>' % htmlescape(char.name)
            if char.sex:
                img = self.call("icon.get", "char-female")
            else:
                img = self.call("icon.get", "char-male")
            ent["INFO"] = '<a href="/character/info/%s" target="_blank"><img src="%s" alt="" class="icon char-info-icon" /></a>' % (char.uuid, img)

    def name_sample_params(self, params):
        params["NAME"] = self._("Character")
        design = self.design("gameinterface")
        params["INFO"] = '<img src="%s" alt="" class="icon char-info-icon" />' % self.call("icon.get", "char-male")

    def name_tokens(self, tokens):
        tokens.append({"id": "NAME", "description": self._("Character name")})
        tokens.append({"id": "INFO", "description": self._("Character info icon")})

    def headmenu_characters_names(self, args):
        if args:
            pinfo = self.call("characters.name-purpose-%s" % args)
            if pinfo:
                return [pinfo["title"], "characters/names"]
            else:
                return [htmlescape(args), "characters/names"]
        return self._("Character names")

    def name_render(self, template, character, params):
        try:
            template = self.call("script.evaluate-text", template, {"char": character})
        except ScriptError:
            template = self.call("script.unparse-text", template)
        if type(template) != unicode:
            template = unicode(template)
        watchdog = 0
        while True:
            watchdog += 1
            if watchdog >= 100:
                break
            try:
                return template.format(**params)
            except KeyError as e:
                params[e.args[0]] = '{?%s?}' % htmlescape(e.args[0])
            except Exception:
                return template
        return template

    def admin_characters_names(self):
        req = self.req()
        self.call("admin.advice", {"title": self._("Character names documentation"), "content": self._('You can find detailed information on the character names system in the <a href="//www.%s/doc/character-names" target="_blank">characer names page</a> in the reference manual.') % self.main_host})
        if req.args:
            pinfo = self.call("characters.name-purpose-%s" % req.args)
            if not pinfo:
                self.call("admin.redirect", "characters/names")
            tokens = []
            self.call("characters.name-tokens", tokens)
            valid_tokens = set()
            for token in tokens:
                valid_tokens.add(token["id"])
            if req.ok():
                errors = {}
                template = req.param("template").strip()
                if not template:
                    errors["template"] = self._("This field is mandatory")
                else:
                    char = self.character(req.user())
                    template = self.call("script.admin-text", "template", errors, {"char": char}, skip_tokens=valid_tokens)
                    tokens = re_tokens.findall(self.call("script.evaluate-text", template, {"char": char}))
                    for token in tokens:
                        if token not in valid_tokens:
                            errors["template"] = self._("Unknown token {%s}") % htmlescape(token)
                            break
                if len(errors):
                    self.call("web.response_json", {"success": False, "errors": errors})
                config = self.app().config_updater()
                config.set("character.name-template-%s" % req.args, template)
                config.store()
                self.app().mc.incr_ver("character-names")
                self.call("admin.redirect", "characters/names")
            else:
                template = self.call("script.unparse-text", self.conf("character.name-template-%s" % pinfo["id"], pinfo["default"]))
            tokens.append({
                "id": self._("script"),
                "description": self._("Ability to use arbitrary scripting expression (for example, show character level: [{char.p_level}])"),
            })
            tokens_html = '<div class="admin-description">%s</div>' % ''.join(['<div><strong>{%s}</strong> &mdash; %s</div>' % (token["id"], token["description"]) for token in tokens])
            fields = [
                {"type": "html", "html": tokens_html},
                {"name": "template", "value": template, "label": '%s%s' % (self._("Name template (valid tags are shown above)"), self.call("script.help-icon-expressions"))},
            ]
            self.call("admin.form", fields=fields)
        purposes = []
        self.call("characters.name-purposes", purposes)
        purposes.sort(cmp=lambda x, y: cmp(x.get("order"), y.get("order")))
        rows = []
        sample_params = {}
        self.call("characters.name-sample-params", sample_params)
        for purp in purposes:
            template = self.conf("character.name-template-%s" % purp["id"], purp["default"])
            rows.append([
                purp["title"],
                self.name_render(template, self.character(req.user()), sample_params),
                '<hook:admin.link href="characters/names/%s" title="%s" />' % (purp["id"], self._("edit")),
            ])
        vars = {
            "tables": [
                {
                    "header": [
                        self._("Purpose"),
                        self._("Format"),
                        self._("Editing"),
                    ],
                    "rows": rows,
                }
            ]
        }
        self.call("admin.response_template", "admin/common/tables.html", vars)

    def headmenu_validate_names(self, args):
        return self._("Names check")

    def admin_validate_names(self):
        req = self.req()
        self.call("admin.advice", {"title": self._("Character names validation"), "content": self._('How to enforce character names validation you can read in the <a href="//www.%s/doc/auth" target="_blank">basic authentication settings</a> manual page') % self.main_host})
        lst = self.objlist(UserList, query_index="check", query_equal="1")
        if req.ok():
            # auth params
            params = {}
            self.call("auth.form_params", params)
            with self.lock(["User.%s" % ent.uuid for ent in lst]):
                errors = {}
                for ent in lst:
                    ent.load()
                    if req.param("ok-%s" % ent.uuid):
                        ent.delkey("check")
                        ent.store()
                    else:
                        name = req.param("name-%s" % ent.uuid)
                        if name:
                            if not re.match(params["name_re"], name, re.UNICODE):
                                errors["name-%s" % ent.uuid] = params["name_invalid_re"]
                            else:
                                existing = self.call("session.find_user", name, return_id=True)
                                if existing and existing != ent.uuid:
                                    errors["name-%s" % ent.uuid] = self._("This name is taken already")
                                else:
                                    ent.delkey("check")
                                    old_name = ent.get("name")
                                    ent.set("name", name)
                                    ent.set("name_lower", name.lower())
                                    ent.store()
                                    if old_name != name:
                                        self.call("auth.name-changed", ent, old_name, name)
                if len(errors):
                    self.call("web.response_json", {"success": False, "errors": errors})
            self.call("admin.redirect", "characters/validate-names")
        lst.load(silent=True)
        if not len(lst):
            self.call("admin.response", self._("All names were checked. Thank you"), {})
        fields = []
        for ent in lst:
            fields.append({"name": "ok-%s" % ent.uuid, "type": "checkbox", "label": self._("Good name"), "desc": htmlescape(ent.get("name"))})
            fields.append({"name": "name-%s" % ent.uuid, "label": self._("Change"), "inline": True, "condition": "![ok-%s]" % ent.uuid})
        self.call("admin.form", fields=fields)

    def character_info_avatar(self, character, vars):
        design = self.design("gameinterface")
        charimage = self.call("charimages.get", character, "charinfo")
        if charimage is None:
            charimage = "/st-mg/constructor/avatars/%s-240x440.jpg" % ("female" if character.sex else "male")
        vars["avatar_image"] = charimage
        self.call("character-info.render", character, vars)
        return self.call("design.parse", design, "character-info-avatar.html", None, vars)

    def character_info(self):
        req = self.req()
        character = self.character(req.args)
        if not character.valid:
            self.call("web.not_found")
        params = []
        vars = {
            "title": htmlescape(character.name),
            "char": ScriptTemplateObject(character),
            "character": {
                "html": character.html(),
                "name": character.name,
                "sex": character.sex,
            }
        }
        vars["character"]["avatar"] = self.call("character.info-avatar", character, vars)
        if not character.restraints.get("hide-info"):
            character_form = self.call("character.form")
            for fld in character_form:
                if not fld.get("std"):
                    code = fld.get("code")
                    if fld.get("type") == 1:
                        val = None
                        val_code = character.db_form.get(code)
                        for ent in fld["values"]:
                            if ent[0] == val_code:
                                val = ent[1]
                                break
                    else:
                        val = re_newline.sub('<br />', htmlescape(character.db_form.get(code)))
                    vars["character"][code] = val
                    if val:
                        params.append({"name": htmlescape(fld.get("name")), "value": val})
        self.call("characters.params-public", character, params)
        if params:
            vars["character"]["params"] = params
        menu = []
        self.call("character.public-info-menu", character, menu)
        if len(menu) >= 2:
            for ent in menu:
                if ent["href"] == "/character/info/%s" % character.uuid:
                    del ent["href"]
            menu.sort(cmp=lambda x, y: cmp(x.get("order", 0), y.get("order", 0)))
            menu[-1]["lst"] = True
            vars["menu"] = menu
        self.call("game.response_external", "character-info.html", vars)

    def character_public_info_menu(self, character, menu):
        menu.append({
            "href": "/character/info/%s" % character.uuid,
            "html": self._("Character information"),
            "order": -10,
        })

    def character_page_avatar(self, character, vars):
        design = self.design("gameinterface")
        charimage = self.call("charimages.get", character, "charpage")
        if charimage is None:
            charimage = "/st-mg/constructor/avatars/%s-120x220.jpg" % ("female" if character.sex else "male")
        vars["avatar_image"] = charimage
        self.call("character-page.render", character, vars)
        return self.call("design.parse", design, "character-page-avatar.html", None, vars)

    def interface_character(self):
        req = self.req()
        character = self.character(req.user())
        actions = []
        self.call("character-page.actions", character, actions)
        actions.sort(cmp=lambda x, y: cmp(x.get("order", 0), y.get("order", 0)))
        vars = {
            "character": {
                "html": character.html(),
                "name": character.name,
                "sex": character.sex,
                "actions": actions or None,
            }
        }
        vars["character"]["avatar"] = self.call("character.page-avatar", character, vars)
        params = []
        self.call("characters.params-owner-important", character, params)
        if params:
            vars["character"]["params"] = params
        self.call("game.response_internal", "character-page.html", vars)

    def interface_character_form(self):
        req = self.req()
        character = self.character(req.user())
        vars = {}
        form = self.call("web.form")
        form.textarea_rows = 6
        fields = self.call("character.form")
        fields = [fld for fld in fields if not fld.get("deleted") and not fld.get("std")]
        values = {}
        if req.ok():
            for fld in fields:
                code = fld["code"]
                val = req.param(code).strip()
                if fld.get("mandatory_level") and not val:
                    form.error(code, self._("This field is mandatory"))
                elif fld.get("type") == 1:
                    if not val and not std and not fld.get("mandatory_level"):
                        # empty value is ok
                        val = None
                    else:
                        # checking acceptable values
                        ok = False
                        for v in fld["values"]:
                            if v[0] == val:
                                ok = True
                                break
                        if not ok:
                            form.error(code, self._("Make a valid selection"))
                values[code] = val
            if not form.errors:
                for fld in fields:
                    code = fld["code"]
                    character.db_form.set(code, values.get(code))
                character.db_form.store()
                self.call("main-frame.info", self._("Information stored"))
        else:
            for field in fields:
                code = field["code"]
                values[code] = character.db_form.get(code)
        for field in fields:
            code = field["code"]
            name = field["name"]
            tp = field.get("type")
            if tp == 1:
                options = [{"value": v, "description": d} for v, d in field["values"]]
                form.select(name, code, values.get(code), options)
            elif tp == 2:
                form.textarea(name, code, values.get(code))
            else:
                form.input(name, code, values.get(code))
        self.call("game.internal_form", form, vars)

    def character_online(self, character):
        character.name_invalidate(update_chat=False)

    def character_offline(self, character):
        character.name_invalidate(update_chat=False)

    def inventory_changed(self, uuid):
        character = self.character(uuid)
        character.name_invalidate()

    def location_changed(self, character, old_location, new_location):
        character.name_invalidate(update_chat=False)

    def characters_param_changed(self, uuid, param, value):
        character = self.character(uuid)
        character.name_invalidate()
        character.send_param(param, value)

    def name_changed(self, user, old_name, new_name):
        character = self.character(user.uuid)
        character.name_invalidate()

    def permissions_changed(self, user):
        character = self.character(user.uuid)
        character.name_invalidate()

    def modifier_created(self, mods, mod):
        character = self.character(mods.uuid)
        if character.valid:
            character.name_invalidate()

    def modifier_destroyed(self, mods, mod):
        character = self.character(mods.uuid)
        if character.valid:
            character.name_invalidate()

    def modifier_expired(self, mods, mod):
        character = self.character(mods.uuid)
        #self.debug("Expired modifier of character %s", character.uuid)
        if character.valid:
            self.call("character-modifier.expired", character, mod)
            character.name_invalidate()
            kind = mod["kind"]
            #self.debug("Expired modifier of kind %s", kind)
            #self.debug("Active modifiers: %s", character.modifiers.mods().keys())
            if not character.modifiers.get(kind):
                if kind.startswith("timer-"):
                    self.qevent("expired-%s" % kind, char=character)
                else:
                    self.qevent("expired-mod-%s" % kind, char=character)

    def character_get(self, uuid):
        return self.character(uuid)
