### Task Description
| Id | Requirement                  | More Details | Status |
| -- | ---------------------------- | ------------ | ------ |
| 1  | Configurable consumer group  | 1. Consumer group with a configurable group size (number of consumers)<br>2. It must be possible to specify the desired group size through command-line arguments or configuration files.   | DONE |
| 2  | Consumer behavior            | 1. Consumer(s) should subscribe to the pre-defined Pub/Sub channel "messages:published".<br>2. Consumers should expect messages in JSON format containing a "message_id" field with a random identifier.<br>3. During startup, the application should create a Redis List with the key name "consumer:ids" and ensure that only active consumer ids are in the list.<br>4. Important! Please consider your solution's scalability. As the number of consumers increases, the message processing throughput should increase. |[!NOTE] Slightly different approach in the solution - the subscribers are registering themselves when they are started<br>DONE |
| 3  | Message processing           | 1. You should implement a function to process the received messages. This can be a simple function that simulates processing by adding a random property and value to a message object.<br>2. Important! Ensure only one consumer within the group processes each message.<br>3. After processing, store the message data (including the "message_id" and any processing results) in a Redis Stream with the key name "messages:processed".<br>4. The stored stream entry in "messages:processed" should also include the consumer's ID that processed the message.    |DONE |
| 4  | Monitoring                  | 1. There should be implemented  logic to periodically (e.g., every 3 seconds) report the current number of messages processed per second.| DONE |
| 5  | Bonus points(optional)      | 1. Provide unit and functional tests for your code.<br>2. Implement it as a distributed system.<br>3. Suggest a better implementation based on the Redis capabilities. | 1. Just a few examples are provided<br>2. Implemented as two microservices.<br>3. Improvements suggestions provided below - based on the current implementation|

### Consumer Application
#### Description
Consumer application represents the actual consumers that are processing the messages - reformatting and enriching the data with consumerId, after that the application adds the enriched message to a Redis Stream.

#### Registration in the Consumer Group Application
After the application is started it calls the ConsumerGroupApplication to register itself as consumer that is available for message processing.

There is a thread running while the application runs to monitor the consumer's registration in the consumer group: each five minutes it checks if the consumer is part of the consumer group - it sends request for registration if it is not part of the group.

#### Rest API
The Consumer application exposes REST Service (implemented with Flask) to allow connections from the ConsumerGroupApplication.
There are two apis exposed:
* /health
  * GET method
  * Allows the consumer group to validate that this consumer is reachable and can be used for message processing
* /processMessage
  * POST method
  * Used to send messages for processing by the Consumer Group Application
  * Expects body with content type 'application/json'
  * Expected body format:
      `{ "message_id": "some_text_guid" }`
  * Returns:
    * Response Code 200 and message for success when message is processed successfully
    * Response Code 400 when the body doesn't match the expected format or is not with content type 'application/json'

#### Scalability
Multiple instances can run in parallel. Just the reported host and port for the REST Service should differ.

### Consumer Group Application
#### Description

#### Registration in the Consumer Group Application

#### Rest API

#### Scalability

### Possible improvements
### How to run services locally
* Configure virtual environment
  * `python3 -m venv .redis_venv`

* Activate the virtual environment
  * `source .redis_venv/bin/activate`

* Install dependencies
  * `pip3 install -r requirements.txt`

* Run Consumer Group Application - there should be just one instance running
  * Redis host and port can be provided as command line parameters(*--redisServerHost \<redisHost\>*, *--redisServerPort \<redisPort\>*) or configured in config file - saved in *consumer_group_app/config/config.properties*
  * Run command example: `python consumer_group_app/src/app.py --maxConsumerGroupSize 10`
* Run Consumer Application
  * Redis host and port can be provided as command line parameters(*--redisServerHost \<redisHost\>*, *--redisServerPort \<redisPort\>*) or configured in config file - saved in `consumer/config/config.properties`
  * If you want to run several instances of the application on the same machine you need to provide different values for rest api port. The configuration can be set through command line parameter (*--restApiPort \<port_value\>*) or in the *config.properties* file located on path *consumer/config/config.properties*
  * Run command example: `python consumer/src/app.py --restApiPort 5001`


