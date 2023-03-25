# tar and start
# tar -xzf kafka_2.13-3.4.0.tgz
cd kafka_2.13-3.4.0

export KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
echo $KAFKA_CLUSTER_ID > ../client_id
cat ../client_id

bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID --cluster-id $KAFKA_CLUSTER_ID -c config/kraft/server.properties --ignore-formatted
nohup bin/kafka-server-start.sh config/kraft/server.properties &

# create topic
bin/kafka-topics.sh --create --topic adops --bootstrap-server localhost:9092

# # write msg
# bin/kafka-console-producer.sh --topic adops --bootstrap-server localhost:9092

# # read msg
# bin/kafka-console-consumer.sh --topic adops --from-beginning --bootstrap-server localhost:9092
