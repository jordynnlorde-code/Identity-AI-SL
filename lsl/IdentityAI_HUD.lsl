// Identity-AI Smart HUD
// Local Chat -> AI Reply
// Touch HUD -> Private AI Chat
// IM sent directly to HUD Object -> AI Reply via IM
// Backend: https://identity-ai-sl.onrender.com/api/hud

string BASE_URL = "https://identity-ai-sl.onrender.com/api/hud";

integer DEBUG = FALSE;

// Public chat
integer CHAT_CHANNEL = 0;

// Owner textbox
integer INPUT_CHANNEL = -777777;

// Distance filter
float MAX_RANGE = 15.0;

// Pending HTTP requests
list pendingRequests = [];

// Request routing
list requestSpeakers = [];
list requestModes = [];

// Reply modes
integer MODE_LOCAL = 0;
integer MODE_PRIVATE = 0;
integer MODE_IM = 0;

//--------------------------------------------------
// Send request to backend
//--------------------------------------------------

sendRequest(key avatarId, string message, integer mode)
{
string payload =
llList2Json(
JSON_OBJECT,
[
"avatar_id",
(string)avatarId,
"message",
message
]
);

```
key req =
    llHTTPRequest(
        BASE_URL,
        [
            HTTP_METHOD,
            "POST",

            HTTP_MIMETYPE,
            "application/json"
        ],
        payload
    );

pendingRequests += [req];
requestSpeakers += [avatarId];
requestModes += [mode];

if (DEBUG)
{
    llOwnerSay("REQUEST:");
    llOwnerSay(payload);
}
```

}

//--------------------------------------------------
// Main
//--------------------------------------------------

default
{
state_entry()
{
llListen(CHAT_CHANNEL, "", NULL_KEY, "");
llListen(INPUT_CHANNEL, "", llGetOwner(), "");

```
    llSetText(
        "Identity-AI HUD\nREADY",
        <0.6,0.8,1.0>,
        1.0
    );

    llOwnerSay("Identity-AI HUD active.");
}

//--------------------------------------------------
// Touch HUD
//--------------------------------------------------

touch_start(integer total_number)
{
    if (llDetectedKey(0) == llGetOwner())
    {
        llTextBox(
            llGetOwner(),
            "Ask Identity-AI:",
            INPUT_CHANNEL
        );
    }
}

//--------------------------------------------------
// Chat + Object IMs
//--------------------------------------------------

listen(integer channel, string name, key id, string msg)
{
    key owner = llGetOwner();

    //--------------------------------------------------
    // Owner private textbox
    //--------------------------------------------------

    if (channel == INPUT_CHANNEL)
    {
        sendRequest(
            owner,
            msg,
            MODE_PRIVATE
        );

        llOwnerSay("AI is thinking...");
        return;
    }

    //--------------------------------------------------
    // Ignore empty text
    //--------------------------------------------------

    if (msg == "")
    {
        return;
    }

    //--------------------------------------------------
    // Ignore objects
    //--------------------------------------------------

    if (llGetAgentSize(id) == ZERO_VECTOR)
    {
        return;
    }

    //--------------------------------------------------
    // Ignore owner's public chat
    //--------------------------------------------------

    if (id == owner)
    {
        return;
    }

    //--------------------------------------------------
    // Distance filter
    //--------------------------------------------------

    vector avatarPos =
        llList2Vector(
            llGetObjectDetails(
                id,
                [OBJECT_POS]
            ),
            0
        );

    if (
        llVecDist(
            llGetPos(),
            avatarPos
        ) > MAX_RANGE
    )
    {
        return;
    }

    //--------------------------------------------------
    // Nearby Chat -> Nearby Reply
    //--------------------------------------------------

    sendRequest(
        id,
        msg,
        MODE_LOCAL
    );
}

//--------------------------------------------------
// HTTP Response
//--------------------------------------------------

http_response(
    key req,
    integer status,
    list meta,
    string body
)
{
    integer idx =
        llListFindList(
            pendingRequests,
            [req]
        );

    if (idx == -1)
    {
        return;
    }

    key speaker =
        llList2Key(
            requestSpeakers,
            idx
        );

    integer mode =
        llList2Integer(
            requestModes,
            idx
        );

    pendingRequests =
        llDeleteSubList(
            pendingRequests,
            idx,
            idx
        );

    requestSpeakers =
        llDeleteSubList(
            requestSpeakers,
            idx,
            idx
        );

    requestModes =
        llDeleteSubList(
            requestModes,
            idx,
            idx
        );

    if (DEBUG)
    {
        llOwnerSay(
            "STATUS: " +
            (string)status
        );

        llOwnerSay(
            "BODY: " +
            body
        );
    }

    //--------------------------------------------------
    // Error
    //--------------------------------------------------

    if (status != 200)
    {
        llOwnerSay(
            "Backend error: " +
            (string)status
        );
        return;
    }

    //--------------------------------------------------
    // Parse reply
    //--------------------------------------------------

    string reply =
        llJsonGetValue(
            body,
            ["reply"]
        );

    if (
        reply == JSON_INVALID ||
        reply == JSON_NULL ||
        llStringTrim(
            reply,
            STRING_TRIM
        ) == ""
    )
    {
        llOwnerSay(
            "Invalid backend response."
        );
        return;
    }

    //--------------------------------------------------
    // Chunk output
    //--------------------------------------------------

    integer chunkSize = 1023;
    integer length = llStringLength(reply);
    integer pos = 0;

    while (pos < length)
    {
        string chunk =
            llGetSubString(
                reply,
                pos,
                pos + chunkSize - 1
            );

        //--------------------------------------------------
        // Nearby chat reply
        //--------------------------------------------------

        if (mode == MODE_LOCAL)
        {
            llSay(0, chunk);
        }

        //--------------------------------------------------
        // Owner textbox -> private reply
        //--------------------------------------------------

        else if (mode == MODE_PRIVATE)
        {
            llOwnerSay(chunk);
        }

        //--------------------------------------------------
        // Direct object IM -> IM reply
        //--------------------------------------------------
        


        else if (mode == MODE_IM)
        {
            llInstantMessage(
                speaker,
                chunk
            );
        }

        pos += chunkSize;

        if (length > chunkSize)
        {
            llSleep(0.5);
        }
    }
}

//--------------------------------------------------
// Reset Safety
//--------------------------------------------------

changed(integer change)
{
    if (change & CHANGED_OWNER)
    {
        llResetScript();
    }
}

on_rez(integer start_param)
{
    llResetScript();
}
```

}
