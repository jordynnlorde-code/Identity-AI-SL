// Identity-AI Smart HUD
// Auto-responds in Local Chat + Owner Textbox
// Backend: https://identity-ai-sl.onrender.com/api/hud

string BASE_URL = "https://identity-ai-sl.onrender.com/api/hud";

integer DEBUG = TRUE;

integer CHAT_CHANNEL = 0;
integer INPUT_CHANNEL = -777777;

float MAX_RANGE = 15.0;

// Prevent excessive concurrent requests
integer MAX_PENDING = 20;

// Track pending HTTP requests
list pendingRequests = [];

default
{
    state_entry()
    {
        llListen(CHAT_CHANNEL, "", NULL_KEY, "");
        llListen(INPUT_CHANNEL, "", llGetOwner(), "");

        llSetText(
            "Identity-AI HUD\nTouch to chat",
            <0.6, 0.8, 1.0>,
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

        // Prevent flooding
        if (llGetListLength(pendingRequests) >= MAX_PENDING)
        {
            if (DEBUG)
            {
                llOwnerSay("Too many pending requests. Please wait.");
            }
            return;
        }

        // ----------------------------------------------------
        // OWNER TEXTBOX
        // ----------------------------------------------------
        if (channel == INPUT_CHANNEL && id == owner)
        {
            string payload =
                llList2Json(
                    JSON_OBJECT,
                    [
                        "avatar_id", (string)owner,
                        "message", msg
                    ]
                );

            key req =
                llHTTPRequest(
                    BASE_URL,
                    [
                        HTTP_METHOD, "POST",
                        HTTP_MIMETYPE, "application/json",
                        HTTP_VERIFY_CERT, TRUE
                    ],
                    payload
                );

            pendingRequests += [req];

            llOwnerSay("AI is thinking...");
            return;
        }

        // ----------------------------------------------------
        // LOCAL CHAT FILTERING
        // ----------------------------------------------------

        // Ignore owner
        if (id == owner)
        {
            return;
        }

        // Ignore objects
        if (llGetAgentSize(id) == ZERO_VECTOR)
        {
            return;
        }

        // Ignore empty messages
        if (msg == "")
        {
            return;
        }

        // Prevent AI-to-AI chat loops
        if (llSubStringIndex(msg, "[AI]") == 0)
        {
            return;
        }

        // Distance filter
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

        // Build JSON payload
        string payload =
            llList2Json(
                JSON_OBJECT,
                [
                    "avatar_id", (string)id,
                    "message", msg
                ]
            );

        if (DEBUG)
        {
            llOwnerSay(
                "Sending message from " +
                name +
                ": " +
                msg
            );
        }

        key req =
            llHTTPRequest(
                BASE_URL,
                [
                    HTTP_METHOD, "POST",
                    HTTP_MIMETYPE, "application/json",
                    HTTP_VERIFY_CERT, TRUE
                ],
                payload
            );

        pendingRequests += [req];
    }

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

        pendingRequests =
            llDeleteSubList(
                pendingRequests,
                idx,
                idx
            );

        if (DEBUG)
        {
            llOwnerSay(
                "HTTP Status: " +
                (string)status
            );

            llOwnerSay(
                "Response: " +
                body
            );
        }

        // ----------------------------------------------------
        // SUCCESS
        // ----------------------------------------------------
        if (status == 200)
        {
            string error =
                llJsonGetValue(
                    body,
                    ["error"]
                );

            if (
                error != JSON_INVALID &&
                error != ""
            )
            {
                llOwnerSay(error);
                return;
            }

            string reply =
                llJsonGetValue(
                    body,
                    ["reply"]
                );

            string remaining =
                llJsonGetValue(
                    body,
                    ["remaining"]
                );

            if (
                reply != JSON_INVALID &&
                reply != ""
            )
            {
                // Prefix prevents HUD feedback loops
                llSay(
                    0,
                    "[AI] " + reply
                );

                if (
                    remaining != JSON_INVALID &&
                    remaining != ""
                )
                {
                    llOwnerSay(
                        "Remaining requests today: " +
                        remaining
                    );
                }
            }
            else
            {
                llOwnerSay(
                    "AI response parsing failed."
                );
            }

            return;
        }

        // ----------------------------------------------------
        // RATE LIMIT
        // ----------------------------------------------------
        if (status == 429)
        {
            llOwnerSay(
                "Identity-AI: Daily limit reached."
            );
            return;
        }

        // ----------------------------------------------------
        // BACKEND ERRORS
        // ----------------------------------------------------
        if (status >= 500)
        {
            llOwnerSay(
                "Identity-AI backend is temporarily unavailable."
            );
            return;
        }

        // ----------------------------------------------------
        // OTHER ERRORS
        // ----------------------------------------------------
        llOwnerSay(
            "Identity-AI error (" +
            (string)status +
            ")"
        );
    }
}