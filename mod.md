# mod loader

## `main.lua`

> mod info

`function love.load()`, before `G:start_up()`

```lua
	if love.filesystem.getInfo('mods') == nil then
		love.filesystem.createDirectory('mods')
	end
	
	local files = love.filesystem.getDirectoryItems('mods')
	for _, mod_name in ipairs(files) do
		local info = love.filesystem.load('mods/'..mod_name..'/info.lua')()
		print('Mod: '..info.name)
	end
```

## `game.lua`

> 增加卡牌

`function Game:init_item_prototypes()`, after the definition of `self.P_CENTERS`

```lua
	local mods = love.filesystem.getDirectoryItems('mods')
	for _, mod_name in ipairs(mods) do
		local items = love.filesystem.load('mods/'..mod_name..'/items.lua')()
		for k, v in pairs(items) do
			G.P_CENTERS[k] = v
		end
	end
```

---

> 增加/替换翻译

`function Game:set_language()`, before `init_localization()` at the end of the function

```lua
      local mods = love.filesystem.getDirectoryItems('mods')
      for _, mod_name in ipairs(mods) do
        local mod_localization_path = 'mods/'..mod_name..'/localization/'..G.SETTINGS.language..'.lua'
        if love.filesystem.exists(mod_localization_path) then
          local mod_localization_data = love.filesystem.load(mod_localization_path)()
          if mod_localization_data ~= nil then
            for outer_category, _ in pairs(self.localization) do
              if mod_localization_data[outer_category] ~= nil then
                for inner_category, _ in pairs(self.localization[outer_category]) do
                  if mod_localization_data[outer_category][inner_category] ~= nil then
                    for k, v in pairs(mod_localization_data[outer_category][inner_category]) do
                      self.localization[outer_category][inner_category][k] = v
                    end
                  end
                end
              end
            end
          end
        end
      end
```

---

> 加载贴图

> 可以做成替换原版的

`function Game:set_render_settings()`, after this section loaded `--Load in all atli defined above`

```lua
    local mods = love.filesystem.getDirectoryItems('mods')
	for _, mod_name in ipairs(mods) do
        local textures = love.filesystem.getDirectoryItems('mods/'..mod_name..'/textures')
        for _, texture_name in ipairs(textures) do
            local texture_bytes = love.filesystem.read('data', 'mods/'..mod_name..'/textures/'..texture_name)
            local texture_image = love.graphics.newImage(texture_bytes)
            local texture_name_without_ext = texture_name:match("([^\\/]+)%.%w+$")
            if texture_image ~= nil then
                self.ASSET_ATLAS['mod_'..texture_name_without_ext] = {}
                self.ASSET_ATLAS['mod_'..texture_name_without_ext].name = texture_name_without_ext
                self.ASSET_ATLAS['mod_'..texture_name_without_ext].image = texture_image
                self.ASSET_ATLAS['mod_'..texture_name_without_ext].px = 71
                self.ASSET_ATLAS['mod_'..texture_name_without_ext].py = 95
            end
        end
	end
```

## `card.lua`

> 卡片指定贴图

> 如果做成替换原版, 这里记得也要改

`function Card:set_sprites(_center, _front)`, in the code block of `elseif _center.set == 'Joker' or _center.consumeable or _center.set == 'Voucher' then`, after `self.children.center`

```lua
                    if _center.order > 150 then
                        self.children.center = Sprite(self.T.x, self.T.y, self.T.w, self.T.h, G.ASSET_ATLAS['mod_'.._center.key], self.config.center.pos)
                    end
```

---

> 小丑牌逻辑

`function Card:calculate_joker(context)`

