local studioservice = game:GetService("StudioService")
local HttpService = game:GetService("HttpService")
local ScriptEditorService = game:GetService("ScriptEditorService")
local toolbar = plugin:CreateToolbar("ironbrew1")
local obfuscatebutton = toolbar:CreateButton("Ironbrew1", "Use Ironbrew1 to obfuscate scripts.", "rbxassetid://79130854450972")
obfuscatebutton.ClickableWhenViewportHidden = true
local options = {
	[1] = "?platform=luau",
	[2] = "&aggressiveOptimizations=2",
	[3] = "&intenseVmScrambling=false",
	[4] = "&antiTamper=false",
	[5] = "&enableVmCompression=false"
}
local opts = ""
for i,v in ipairs(options) do
	opts = opts .. v
end

local function encryptdata(str) -- Better to not have it in plain text lol even if it's easy to crack :)
	local len = str:len()
	local new = ""
	for i = 1, len do
		if len > i then
			new = new .. string.byte(str, i).."/"
		else
			new = new .. string.byte(str, i)
		end
	end
	return new
end

local function decryptdata(str)
	local encrypted = str:split("/")
	local new = ""
	for i,v in pairs(encrypted) do
		new = new .. string.char(v)
	end
	return new
end

local function getClientId()
	local clientId = plugin:GetSetting("IB1ClientId")

	if type(clientId) ~= "string" or #clientId < 8 then
		clientId = "roblox-plugin:" .. HttpService:GenerateGUID(false)
		plugin:SetSetting("IB1ClientId", clientId)
	end

	return clientId
end

function openapikeyprompt()
	if game:GetService("CoreGui"):FindFirstChild("InputAPIKey") then warn("Sign-in prompt already open.") return end
	signin = script.InputAPIKey:Clone()
	signin.Archivable = false
	signin.Parent = game:GetService("CoreGui")
	signin["Sign-in"].Save.mouseButton1Click:Connect(function()
		plugin:SetSetting("IB1KEY", encryptdata(signin["Sign-in"].KEY.Text))
		signin:Destroy()
	end)
end

local function checks(scripttype)
	if not plugin:GetSetting("IB1KEY") then
		openapikeyprompt()
		return false
	end
	if scripttype then
		if not scripttype:IsA("ModuleScript") then
			return true
		else
			warn("ModuleScripts are not supported.")
			return false
		end
	else
		warn("Open a script before obfuscating.")
		return false
	end
end

obfuscatebutton.Click:Connect(function()
	if checks(studioservice.ActiveScript) then
		local obfuscateSuccess, obfuscateResponse = pcall(function()
			return HttpService:RequestAsync({
				Url = "https://ironbrew1.com/obfuscate",
				Method = "POST",
				Headers = {
					["Key"] = decryptdata(plugin:GetSetting("IB1KEY")),
					["Content-Type"] = "text/plain",
					["X-IB1-Client-Id"] = getClientId()
				},
				Body = studioservice.ActiveScript.Source
			})
		end)
		if obfuscateSuccess and obfuscateResponse.Success then
			local newscript = Instance.new(studioservice.ActiveScript.ClassName)
			ScriptEditorService:UpdateSourceAsync(newscript, function()
				return obfuscateResponse.Body
			end)
			newscript.Parent = studioservice.ActiveScript.Parent
			newscript.Name = studioservice.ActiveScript.Name.." (OBFUSCATED)"
			plugin:OpenScript(newscript)
		else
			warn("Obfuscation Failed (" .. tostring(obfuscateResponse.StatusCode) .. ") " .. tostring(obfuscateResponse.Body))
			if obfuscateResponse.StatusCode == 401 then
				warn("This error is related to authentication please ensure your API key and subscription are both valid.")
				plugin:SetSetting("IB1KEY", nil)
				openapikeyprompt()
			end
		end
	end
end)

plugin.Unloading:Connect(function()
	if signin then
		signin:Destroy()
	end
end)
