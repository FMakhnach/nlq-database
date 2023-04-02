from datetime import datetime, timedelta

testcases = [
    {
        "title": "General question",
        "subcases": [
            {
                "enabled": False,
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
        "title": "Event tied to a point in time",
        "subcases": [
            {
                #"enabled": False,
                "title": "Dentist appointment",
                "dialog": [
                    {
                        "enabled": False,
                        "Q": "I need to buy apples, milk, tomatoes and eggs. Write it down.",
                        "A": "Ok, got it."
                    },
                    {
                        "enabled": False,
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

'''

Write json schema for such a message:

{
    "user_id": 123456,
    "appointments": [
        {
            "type": "dentist",
            "date": "2023-03-22",
            "time": "10:00"
        }
    ],
    "shopping_list": [
        {"item": "apples", "is_bought": false },
        {"item": "milk", "is_bought": false },
        {"item": "tomatoes", "is_bought": true }
    ],
    "weights": [
        {"weight_kg": 78.8, "moment": "2023-03-20T12:37:23"},
        {"weight_kg": 79.3, "moment": "2023-03-23T10:11:27"},
        {"weight_kg": 78.8, "moment": "2023-03-20T12:37:23"},
        {"weight_kg": 79.3, "moment": "2023-03-23T10:11:27"},
        {"weight_kg": 78.8, "moment": "2023-03-20T12:37:23"},
        {"weight_kg": 79.3, "moment": "2023-03-23T10:11:27"},
        {"weight_kg": 78.8, "moment": "2023-03-20T12:37:23"},
        {"weight_kg": 79.3, "moment": "2023-03-23T10:11:27"},
        {"weight_kg": 78.8, "moment": "2023-03-20T12:37:23"},
        {"weight_kg": 79.3, "moment": "2023-03-23T10:11:27"},
        {"weight_kg": 78.8, "moment": "2023-03-20T12:37:23"},
        {"weight_kg": 79.3, "moment": "2023-03-23T10:11:27"},
        {"weight_kg": 78.8, "moment": "2023-03-20T12:37:23"},
        {"weight_kg": 79.3, "moment": "2023-03-23T10:11:27"},
        {"weight_kg": 78.8, "moment": "2023-03-20T12:37:23"},
        {"weight_kg": 79.3, "moment": "2023-03-23T10:11:27"},
    ]
}

{
  "appointments": {
    "type": "list",
    "element_type": {
      "type": "string",
      "date": "date",
      "time": "time"
    }
  },
  "shopping_list": {
      "type": "list",
      "element_type": {
        ""
      }
    }
}

{
    "user_id": 1234,
    "data": {
        "appointments": [
            {
                "type": "dentist",
                "date": "2023-03-22",
                "time": "10:00"
            }
        ],
        "shopping_list": [
            {"item": "apples", "is_bought": false },
            {"item": "milk", "is_bought": false },
            {"item": "tomatoes", "is_bought": true }
        ],
        "weights": [
            {"weight_kg": 78.8, "moment": "2023-03-20T12:37:23"},
            {"weight_kg": 79.3, "moment": "2023-03-23T10:11:27"},
        ]
    }
}    

'''

