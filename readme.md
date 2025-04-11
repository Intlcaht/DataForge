 ITLC System Database Architecture

This system consists of multiple databases supporting various functionalities across users, services, orders, content, tokens, templates, and workflows.
🧑‍💼 itlc_users Database
Users

Stores information about users of the platform.
Field	Type	Description
id	SERIAL PK	Unique user ID (Primary Key)
name	VARCHAR	Full name
email	VARCHAR	Unique email
password	VARCHAR	Hashed password
tokens	INTEGER	Token balance
created_at	TIMESTAMP	User creation time
updated_at	TIMESTAMP	Last update time
📦 itlc_pbfr Database
Projects

Represents user-generated projects.
Field	Type	Description
_id	ObjectId PK	Unique identifier
name	String	Project name
description	String	Project details
created_at	ISODate	Creation time
Blogs

Optional blog posts from providers.
Field	Type	Description
_id	ObjectId PK	Blog ID
title	String	Blog title
content	String	Blog content
author	String	Author name
created_at	ISODate	Creation timestamp
FAQs

Provider-submitted frequently asked questions.
Field	Type	Description
_id	ObjectId PK	FAQ ID
question	String	The question
answer	String	The answer
created_at	ISODate	Creation date
Ratings

Ratings provided by users.
Field	Type	Description
_id	ObjectId PK	Rating ID
rating	Number	Rating score
review	String	Textual review
created_at	ISODate	When it was given
Reviews

User feedback independent of ratings.
Field	Type	Description
_id	ObjectId PK	Review ID
review	String	Review content
created_at	ISODate	Review date
🛠 itlc_api Database
Services

Defines services offered by providers.
Field	Type	Description
id	SERIAL PK	Unique service ID
name	VARCHAR	Name of service
description	TEXT	Details
provider_id	INTEGER FK	Linked to Providers
created_at	TIMESTAMP	Service creation timestamp
updated_at	TIMESTAMP	Last updated timestamp
Providers

Entities offering services.
Field	Type	Description
id	SERIAL PK	Unique provider ID
name	VARCHAR	Provider name
email	VARCHAR	Unique email
created_at	TIMESTAMP	When they joined
updated_at	TIMESTAMP	Last updated
📦 itlc_orders Database
Orders

Orders placed by users for services.
Field	Type	Description
id	SERIAL PK	Unique order ID
user_id	INTEGER FK	Linked to Users
service_id	INTEGER FK	Linked to Services
amount	DECIMAL	Payment amount
status	VARCHAR	Current status
created_at	TIMESTAMP	Creation time
Notifications

Messages for users.
Field	Type	Description
id	SERIAL PK	Unique notification ID
user_id	INTEGER FK	Linked to Users
message	TEXT	Notification content
read_status	BOOLEAN	Whether read or not
created_at	TIMESTAMP	Notification creation time
Bidding

Bids placed on services.
Field	Type	Description
id	SERIAL PK	Unique bid ID
order_id	INTEGER FK	Associated Order
bidder_id	INTEGER FK	User or provider placing bid
amount	DECIMAL	Bid amount
created_at	TIMESTAMP	Bid creation time
Checkins

Stepwise progress or logs of service execution.
Field	Type	Description
id	SERIAL PK	Unique check-in ID
order_id	INTEGER FK	Associated Order
status	VARCHAR	Status of check-in
created_at	TIMESTAMP	When the check-in was made
💰 itlc_tokens Database
Token Top-Up

Tracks token purchases.
Field	Type	Description
id	SERIAL PK	Top-up ID
user_id	INTEGER FK	Linked user
amount	DECIMAL	Amount of tokens
status	VARCHAR	Top-up status
created_at	TIMESTAMP	Timestamp of top-up
📋 itlc_templates Database
Template Store

Templates for creating projects or services.
Field	Type	Description
id	SERIAL PK	Template ID
name	VARCHAR	Name
description	TEXT	What it's used for
type	VARCHAR	Project or service
created_at	TIMESTAMP	Template creation date
updated_at	TIMESTAMP	Last modification date
🧠 neo4j Graph Database
Order Steps

Represents stepwise execution plans for orders.
Field	Type	Description
id	UUID PK	Unique step ID
order_id	INTEGER FK	Linked order
step_number	INTEGER	Sequence number
description	TEXT	Step detail
requirements	TEXT	Required elements
notified_personnel	TEXT	Who to notify
created_at	TIMESTAMP	Timestamp
🔁 Inter-Database Relationships & Workflow

    Users create Projects.

    Projects use Services from the itlc_api database.

    Users can bid on services and view bids.

    Providers create Orders from bids and update them via Checkins.

    Users pay for completed Projects.

    Providers can optionally create Blogs and FAQs.

    Users provide Ratings and Reviews.

    Providers can top up tokens, which updates user balances.

    Users can select Templates, which are used to create Projects and Services.

    Providers define Order Steps (Neo4j), which notify users via Notifications and connect to Orders.