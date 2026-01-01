# Payment Service - Dapr Configuration

## Ports
- **App Port**: 8002
- **Dapr HTTP Port**: 3502
- **Dapr gRPC Port**: 50002
- **Dapr Metrics Port**: 9092

## Dapr Components Used
- **PubSub**: `imtiaz-pubsub` (shared Kafka pubsub)

## Topics Published
- `payment.initiated` - When payment is created
- `payment.completed` - When payment is successfully completed
- `payment.failed` - When payment fails
- `payment.refunded` - When payment is refunded

## Topics Subscribed
- (To be added when implementing order integration)
