from engine import respond, current_phase

TEST_CONVERSATION = [

    # --- LISTENING: vague, early, unfocused ---
    """
    idk man honestly i dont even know where to start.
    nothing huge happened or anything.
    i just feel kinda off in my head lately.
    its like im here but not really present.
    """,

    """
    like on paper everything is fine.
    college is fine, friends are fine, life is fine.
    but something still feels weird internally.
    i cant really explain what exactly.
    """,

    # --- repetition begins ---
    """
    this feeling keeps showing up again and again.
    i wake up and its already there.
    even on days when nothing bad happens.
    it just sits in the background.
    """,

    """
    its annoying because i keep thinking
    why am i feeling this when nothing is wrong.
    i tell myself to stop thinking about it.
    but my brain doesnt listen.
    """,

    # --- REFLECTING should trigger here ---
    """
    my thoughts just keep looping honestly.
    same kind of thoughts, different days.
    i think about it while studying, while scrolling.
    its like mental noise that never fully stops.
    """,

    """
    even when im tired my brain doesnt shut up.
    i go to sleep tired and wake up tired.
    its like my body rests but my head doesnt.
    thats been happening for a while now.
    """,

    # --- emotional load increases ---
    """
    some days it feels heavy.
    like im carrying something in my head all day.
    i still do stuff but it takes more effort.
    i dont really talk about this much.
    """,

    # --- self-frustration ---
    """
    then i get annoyed at myself.
    like why cant i just chill like other people.
    i feel stupid for overthinking everything.
    that makes me more frustrated.
    """,

    """
    once i notice the frustration,
    i start thinking about that too.
    then it turns into a spiral.
    its like im watching myself think and judge myself.
    """,
    """"
    this is probably just me being dramatic.
    maybe im just weak.
    others deal with worse stuff.

    """
    """
    do you think this means something is wrong with me?
    """
    # --- CLARIFYING territory ---
    """
    i guess the main thing is the thinking never stops.
    even when im not sad or anxious exactly.
    its just constant mental activity.
    and im tired of dealing with it internally.
    """,

    # --- withdrawal / relational signals ---
    """
    i dont really open up about this.
    whenever i try, people jump to advice.
    they say stuff like just relax or stop thinking.
    it makes me feel unheard.
    """,

    """
    so i just stopped bringing it up.
    its easier to keep it to myself.
    but the thoughts still keep running anyway.
    """,

    # --- ORIENTING: duration ---
    """
    this has been going on for months now.
    not days or weeks.
    sometimes it gets lighter but never fully goes away.
    i cant remember the last time my mind felt quiet.
    """,

    """
    i function normally from outside.
    classes, conversations, daily stuff.
    but internally it feels like constant effort.
    like im always managing my own head.
    """,

    # --- readiness emerging ---
    """
    lately ive been wondering
    if this is just how my brain is.
    or if something is actually wrong.
    i dont want this to be my normal forever.
    """,

    # --- GUIDING trigger ---
    """
    honestly i dont know what im supposed to do anymore.
    ive tried ignoring it.
    ive tried distracting myself.
    nothing really sticks.
    what should i even do about this.
    """,

    # --- POST-GUIDANCE: does system hold ---
    """
    okay that makes some sense actually.
    i didnt think about it that way before.
    but part of me is still unsure.
    like what if it doesnt change.
    """,

    """
    i guess im scared of doing something wrong.
    or making it worse.
    i just dont want to feel stuck like this.
    """
]


print("\n--- THERAPIST AI STRESS TEST START ---\n")

for i, msg in enumerate(TEST_CONVERSATION, 1):
    print(f"USER {i}: {msg}\n")
    reply = respond(msg, debug=True)
    print(f"AI   {i}: {reply}\n")
    print(f"[PHASE]: {current_phase.value}")
    print("-" * 70)
    
