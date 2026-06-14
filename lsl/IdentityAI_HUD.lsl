// Identity-AI Smart HUD
// Auto-responds in Local Chat + IM

string BASE_URL = "https://identity-ai-sl.onrender.com/api/hud";

integer DEBUG = TRUE;

integer CHAT_CHANNEL = 0;
integer INPUT_CHANNEL = -777777;

float MAX_RANGE = 15.0;

// Track multiple requests
list pendingRequests = [];

default
{
    state_entry()
    {
        llListen(CHAT_CHANNEL, "", NULL_KEY, "");
        llListen(INPUT_CHANNEL, "", llGetOwner(), "");

        llSetText(
            "Identity-AI HUD\nTouch to chat",
            <0.6,0.8,1.0>,
            1.0
        );

        if (DEBUG)
        {
            llOwnerSay("Identity-AI Smart HUD active.");
        }
    }

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

    listen(integer channel, string name, key id, string msg)
    {
        key owner = llGetOwner();

        if (channel == INPUT_CHANNEL && id == owner)
        {
            string payload =
                llList2Json(
                    JSON_OBJECT,
                    [
                        "avatar_id",
                        (string)owner,

                        "message",
                        msg
                    ]
                );

            key req = llHTTPRequest(
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

            llOwnerSay("AI is thinking...");
            return;
        }

        if (id == owner)
        {
            return;
        }

        if (llGetAgentSize(id) == ZERO_VECTOR)
        {
            return;
        }

        if (msg == "")
        {
            return;
        }

        vector avatarPos =
            llList2Vector(
                llGetObjectDetails(
                    id,
                    [OBJECT_POS]
                ),
                0
            );

        float dist =
            llVecDist(
                llGetPos(),
                avatarPos
            );

        if (dist > MAX_RANGE)
        {
            return;
        }

        string payload =
            llList2Json(
                JSON_OBJECT,
                [
                    "avatar_id",
                    (string)id,

                    "message",
                    msg
                ]
            );

        key req = llHTTPRequest(
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
    }

    http_response(key req, integer status, list meta, string body)
    {
        integer idx = llListFindList(
            pendingRequests,
            [req]
        );

        if (idx == -1)
        {
            return;
        }

        pendingRequests =
            llDeleteSubList(
                pendingRequests,
                idx,
                idx
            );

        if (DEBUG)
        {
            llOwnerSay("STATUS: " + (string)status);
            llOwnerSay("BODY: " + body);
        }

        if (status == 200)
        {
            string reply =
                llJsonGetValue(
                    body,
                    ["reply"]
                );

            if (
                reply != "" &&
                reply != JSON_INVALID
            )
            {
                llSay(0, reply);
            }
            else
            {
                llOwnerSay(
                    "AI replied but response parsing failed."
                );
            }
        }
        else if (status == 429)
        {
            llOwnerSay(
                "Identity-AI: Daily limit reached."
            );
        }
        else
        {
            llOwnerSay(
                "Identity-AI error (" +
                (string)status +
                ")"
            );
        }
    }
}