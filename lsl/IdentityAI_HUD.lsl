// Identity‑AI Smart HUD
// Auto‑responds in Local Chat + IM
// Backend: https://identity-ai-sl.onrender.com/api/hud

string BASE_URL = "https://identity-ai-sl.onrender.com/api/hud";
integer DEBUG   = TRUE;

// Local chat listen channel
integer CHAT_CHANNEL = 0;

// Private channel for owner text input
integer INPUT_CHANNEL = -777777;

// Max distance for auto‑response
float MAX_RANGE = 15.0;

key lastReq;

// -----------------------------
// JSON Helpers
// -----------------------------
string buildJSON(string avatar, string message)
{
    message = llEscapeURL(message);
    return "{\"avatar_id\":\"" + avatar + "\",\"message\":\"" + message + "\"}";
}

string json_extract(string body, string key)
{
    string pattern = "\"" + key + "\":\"";
    integer start = llSubStringIndex(body, pattern);
    if (start == -1) return "";

    start += llStringLength(pattern);
    integer end = llSubStringIndex(llGetSubString(body, start, -1), "\"");
    if (end == -1) return "";

    return llGetSubString(body, start, start + end - 1);
}

// -----------------------------
// LSL Events
// -----------------------------
default
{
    state_entry()
    {
        llListen(CHAT_CHANNEL, "", NULL_KEY, "");
        llListen(INPUT_CHANNEL, "", llGetOwner(), "");

        llSetText("Identity‑AI HUD\nTouch to chat ✨", <0.6,0.8,1.0>, 1.0);

        if (DEBUG)
            llOwnerSay("Identity‑AI Smart HUD active.");
    }

    touch_start(integer n)
    {
        if (llDetectedKey(0) == llGetOwner())
            llTextBox(llGetOwner(), "Ask Identity‑AI:", INPUT_CHANNEL);
    }

    // -----------------------------
    // LOCAL CHAT + OWNER TEXTBOX
    // -----------------------------
    listen(integer channel, string name, key id, string msg)
    {
        key owner = llGetOwner();

        // Owner text input → always allowed
        if (channel == INPUT_CHANNEL && id == owner)
        {
            string json = buildJSON((string)owner, msg);

            if (DEBUG)
                llOwnerSay("Sending (owner): " + json);

            lastReq = llHTTPRequest(
                BASE_URL,
                ["Content-Type","application/json"],
                json
            );

            llOwnerSay("AI is thinking…");
            return;
        }

        // Local chat → ignore owner
        if (id == owner) return;

        // Ignore objects
        if (llGetAgentSize(id) == ZERO_VECTOR) return;

        // Distance filter
        float dist = llVecDist(llGetPos(), llList2Vector(llGetObjectDetails(id, [OBJECT_POS]), 0));
        if (dist > MAX_RANGE) return;

        // Ignore empty messages
        if (msg == "") return;

        // Build JSON
        string json = buildJSON((string)id, msg);

        if (DEBUG)
            llOwnerSay("Sending (local): " + json);

        lastReq = llHTTPRequest(
            BASE_URL,
            ["Content-Type","application/json"],
            json
        );
    }

    // -----------------------------
    // HTTP RESPONSE
    // -----------------------------
    http_response(key req, integer status, list meta, string body)
    {
        if (req != lastReq)
        {
            if (DEBUG)
                llOwnerSay("Ignoring old response.");
            return;
        }

        if (DEBUG)
        {
            llOwnerSay("STATUS: " + (string)status);
            llOwnerSay("BODY: " + body);
        }

        if (status == 200)
        {
            string reply = json_extract(body, "reply");
            reply = llUnescapeURL(reply);

            if (reply != "")
            {
                // Speak in local chat
                llSay(0, reply);
            }
            else
            {
                llOwnerSay("AI replied but parsing failed.");
            }
        }
        else if (status == 429)
        {
            llOwnerSay("Identity‑AI: Daily limit reached (30 messages).");
        }
        else
        {
            llOwnerSay("Identity‑AI error (" + (string)status + "): " + body);
        }
    }
}
