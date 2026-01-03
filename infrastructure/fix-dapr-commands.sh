#!/bin/bash

echo "🔧 Fixing Dapr command formats..."

# Backup
cp docker-compose.yml docker-compose.yml.backup.dapr-fix

# Use sed to replace command arrays with single string format
# This is complex, so better to do manually, but here's the pattern

echo "Manual fix required. Please update each *-service-dapr command section:"
echo ""
echo "CHANGE FROM:"
echo '  command: ['
echo '    "./daprd",'
echo '    "-app-id", "service-name",'
echo '    ...'
echo '  ]'
echo ""
echo "CHANGE TO:"
echo '  command: >-'
echo '    ./daprd'
echo '    -app-id service-name'
echo '    -app-port PORT'
echo '    -dapr-http-port PORT'
echo '    ...'
echo ""
echo "See dapr-fixed-template.yml for complete examples"

# Create template file
cat > dapr-fixed-template.yml << 'TEMPLATE'
# ==========================================
# CORRECTED DAPR SIDECARS - USE THESE
# ==========================================

  user-service-dapr:
    image: daprio/daprd:latest
    container_name: imtiaz-user-service-dapr
    command: >-
      ./daprd
      -app-id user-service
      -app-port 8000
      -dapr-http-port 3500
      -dapr-grpc-port 50000
      -dapr-metrics-port 9090
      -components-path /components
      -config /config/config.yaml
      -log-level debug
    volumes:
      - ./dapr/components:/components:ro
      - ./dapr/config.yaml:/config/config.yaml:ro
    depends_on:
      - user-service
      - kafka
    network_mode: "service:user-service"
    restart: unless-stopped

  product-service-dapr:
    image: daprio/daprd:latest
    container_name: imtiaz-product-service-dapr
    command: >-
      ./daprd
      -app-id product-service
      -app-port 8001
      -dapr-http-port 3501
      -dapr-grpc-port 50001
      -dapr-metrics-port 9091
      -components-path /components
      -config /config/config.yaml
      -log-level debug
    volumes:
      - ./dapr/components:/components:ro
      - ./dapr/config.yaml:/config/config.yaml:ro
    depends_on:
      - product-service
      - kafka
    network_mode: "service:product-service"
    restart: unless-stopped

  payment-service-dapr:
    image: daprio/daprd:latest
    container_name: imtiaz-payment-service-dapr
    command: >-
      ./daprd
      -app-id payment-service
      -app-port 8002
      -dapr-http-port 3502
      -dapr-grpc-port 50002
      -dapr-metrics-port 9092
      -components-path /components
      -config /config/config.yaml
      -log-level debug
    volumes:
      - ./dapr/components:/components:ro
      - ./dapr/config.yaml:/config/config.yaml:ro
    depends_on:
      - payment-service
      - kafka
    network_mode: "service:payment-service"
    restart: unless-stopped

  order-service-dapr:
    image: daprio/daprd:latest
    container_name: imtiaz-order-service-dapr
    command: >-
      ./daprd
      -app-id order-service
      -app-port 8003
      -dapr-http-port 3503
      -dapr-grpc-port 50003
      -dapr-metrics-port 9093
      -components-path /components
      -config /config/config.yaml
      -log-level debug
    volumes:
      - ./dapr/components:/components:ro
      - ./dapr/config.yaml:/config/config.yaml:ro
    depends_on:
      - order-service
      - kafka
    network_mode: "service:order-service"
    restart: unless-stopped

  inventory-service-dapr:
    image: daprio/daprd:latest
    container_name: imtiaz-inventory-service-dapr
    command: >-
      ./daprd
      -app-id inventory-service
      -app-port 8004
      -dapr-http-port 3504
      -dapr-grpc-port 50004
      -dapr-metrics-port 9094
      -components-path /components
      -config /config/config.yaml
      -log-level debug
    volumes:
      - ./dapr/components:/components:ro
      - ./dapr/config.yaml:/config/config.yaml:ro
    depends_on:
      - inventory-service
      - kafka
    network_mode: "service:inventory-service"
    restart: unless-stopped

TEMPLATE

echo "✅ Template created: dapr-fixed-template.yml"
echo ""
echo "Next steps:"
echo "1. Open docker-compose.yml in your editor"
echo "2. Find each '*-service-dapr:' section"
echo "3. Replace the 'command: [...]' with 'command: >-' format from template"
echo "4. Save and run: docker-compose up -d"
