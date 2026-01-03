from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import threading
import time
import random
import requests

SERVICE_TOKEN = "async-dehydration-8bytes-key"
MAIN_SERVICE_URL = "http://localhost:8082/api/async/result"
DELAY_SECONDS = 7

class CalculateView(APIView):
    def post(self, request):
        request_id = request.data.get('request_id')
        patient_weight = request.data.get('patient_weight')
        if not request_id or not patient_weight:
            return Response({'error': 'request_id and patient_weight required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Запускаем расчет в отдельном потоке
        threading.Thread(target=self.process_calculation, args=(request_id, patient_weight)).start()
        return Response({'status': 'accepted', 'message': f'Calculation will complete in ~{DELAY_SECONDS} seconds', 'request_id': request_id}, status=status.HTTP_202_ACCEPTED)

    def process_calculation(self, request_id, patient_weight):
        time.sleep(DELAY_SECONDS)
        dehydration_percent = self.calculate_dehydration_percent(float(patient_weight))
        payload = {
            'request_id': request_id,
            'dehydration_percent': dehydration_percent,
            'service_token': SERVICE_TOKEN
        }
        try:
            resp = requests.post(MAIN_SERVICE_URL, json=payload)
        except Exception as e:
            print(f'Error sending result: {e}')

    def calculate_dehydration_percent(self, patient_weight):
        base_percent = 3.0 + random.random() * 9.0
        weight_factor = 1.0
        if patient_weight < 20:
            weight_factor = 1.3
        elif patient_weight > 100:
            weight_factor = 0.8
        result = base_percent * weight_factor
        return round(result, 2)

# Create your views here.
