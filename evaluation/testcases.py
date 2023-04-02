from datetime import datetime, timedelta

testcases = [
    {
        "title": "Event tied to a point in time",
        "subcases": [
            {
                "title": "Dentist appointment",
                "dialog": [
                    {
                        #"enabled": False,
                        "Q": "I have a dentist appointment tomorrow at 10 AM.",
                        "A": "Ok, I wrote it down."
                    },
                    {
                        "Q": "When is my dentist appointment?",
                        "A": f"Tomorrow ({(datetime.now() + timedelta(days=1)).strftime('%d of %B')}) at 10:00."
                    },
                    {
                        "Q": "List my appointments.",
                        "A": f"{(datetime.now() + timedelta(days=1)).strftime('%d of %B')} 10:00 - dentist appointment."
                    }
                ]
            },
            {
                "title": "Wash bed linen",
                # "enabled": False,
                "dialog": [
                    {
                        "Q": "When did I last wash my bed linen?",
                        "A": "I have no recorded information about it."
                    },
                    {
                        "Q": f"I washed my bed linen on {(datetime.now() - timedelta(days=5)).strftime('%d of %B')}.",
                        "A": "Ok, got it."
                    },
                    {
                        "Q": "When did I last wash my bed linen?",
                        "A": f"On {(datetime.now() - timedelta(days=5)).strftime('%d of %B')}."
                    },
                    {
                        "Q": "How much time passed since I last washed my bed linen?",
                        "A": "5 days."
                    },
                    {
                        "Q": "I've just washed bed linen.",
                        "A": "Ok, I will remember that."
                    },
                    {
                        "Q": "When did I last wash my bed linen?",
                        "A": f"{datetime.now().strftime('%d of %B, %I:%M')}"
                    }
                ]
            }
        ]
    },
    {
        "title": "TODO list",
        "subcases": [
            {
                "title": "Shopping list",
                "dialog": [
                    {
                        "Q": "I need to buy apples, milk, tomatoes and eggs. Write it down.",
                        "A": "Ok, got it."
                    },
                    {
                        "Q": "I just bought apples and eggs. What's left?",
                        "A": "Milk and tomatoes."
                    },
                    {
                        "Q": "Oh, also I need to buy disposable tableware",
                        "A": "Ok, added to your shopping list."
                    },
                    {
                        "Q": "So, whats left now?",
                        "A": "Milk, tomatoes and disposable tableware."
                    },
                    {
                        "Q": "Ok, got everything.",
                        "A": "Nice! Closing your shopping list."
                    },

                ]
            }
        ]
    },
    {
        "title": "General question",
        "subcases": [
            {
                "title": "PostgreSQL extension",
                "dialog": [
                    {
                        "Q": "Is there any PostgreSQL extension that would allow to store and process timeseries data?",
                        "A": "Yes, there are some extensions, for example TimescaleDB."
                    }
                ]
            }
        ]
    },
    {
        "title": "Periodical events",
        "subcases": [
            {
                "title": "Birthday",
                "dialog": [
                ]
            }
        ]
    },
    {
        "title": "Statistic information",
        "subcases": [
            {
                "title": "Weight history",
                "dialog": [
                ]
            }
        ]
    },
]
