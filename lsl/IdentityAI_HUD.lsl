// Identity‑AI HUD (Groq) - Final working version
string BASE_URL = "https://identity-ai-sl.onrender.com/api/hud";
integer CHANNEL = 7777;
integer DEBUG = TRUE;

key lastReq;

string buildJSON(string avatar, string message)
{
    // Only escape the message content
    message = llEscapeURL(message);
    return "{\"avatar_id\":\"" + avatar + "\",\"message\":\"" + message + "\"}";
}

default
{
    state_entry()
    {
        llListen(CHANNEL, "", llGetOwner(), "");
        llSetText("Identity‑AI HUD\nTouch to chat ✨", <1,1,1>, 1.0);
    }

    touch_start(integer n)
    {
        if (llDetectedKey(0) == llGetOwner())
        {
            llTextBox(llGetOwner(), "Ask Identity‑AI:", CHANNEL);
        }
    }

    listen(integer ch, string nm, key id, string msg)
    {
        if (msg == "") return;

        string json = buildJSON((string)llGetOwner(), msg);

        list headers = [
            "Content-Type", "application/json"
        ];

        if (DEBUG)
        {
            llOwnerSay("Sending JSON: " + json);
        }

        lastReq = llHTTPRequest(BASE_URL, headers, json);
        llOwnerSay("Thinking…");
    }

    http_response(key req, integer status, list meta, string body)
    {
        if (DEBUG)
        {
            llOwnerSay("REQ: " + (string)req);
            llOwnerSay("LAST: " + (string)lastReq);
            llOwnerSay("STATUS: " + (string)status);
            llOwnerSay("BODY: " + body);
        }

        if (req != lastReq) return;

        if (status == 200)
        {
            integer i = llSubStringIndex(body, "\"reply\":\"");
            if (i != -1)
            {
                integer start = i + 9;
                integer end = llSubStringIndex(llGetSubString(body, start, -1), "\"");
                if (end != -1)
                {
                    string reply = llGetSubString(body, start, start + end - 1);
                    reply = llUnescapeURL(reply);
                    llOwnerSay("AI: " + reply);
                    return;
                }
            }
            llOwnerSay("Got a response but couldn't parse it.");
        }
        else if (status == 429)
        {
            llOwnerSay("You've reached your daily limit (30).");
        }
        else
        {
            llOwnerSay("Error (" + (string)status + "): " + body);
        }
    }
}
