// script.js

document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';

    // 1. Enviar la petición POST
    try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/classify/', {
            method: 'POST',
            body: formData, // FormData envía automáticamente multipart/form-data
        });

        const data = await response.json();

        if (response.ok) {
            // 2. Procesar y Mostrar Resultados
            const diagnosis = data.tumor_present === 1 ? 'Posible Tumor Detectado' : 'No se detectó tumor';
            
            document.getElementById('diagnosis').textContent = diagnosis;
            document.getElementById('confidence').textContent = `${(data.confidence * 100).toFixed(2)}%`;

            // 3. Decodificar y mostrar imágenes Base64
            // El prefijo 'data:image/png;base64,' es necesario para el navegador
            document.getElementById('img-original').src = `data:image/png;base64,${data.original_image_base64}`;
            document.getElementById('img-analyzed').src = `data:image/png;base64,${data.analyzed_image_base64}`;

            document.getElementById('results').style.display = 'block';
        } else {
            alert(`Error en la API: ${data.error || data.detail}`);
        }

    } catch (error) {
        console.error('Error al realizar la petición:', error);
        alert('Ocurrió un error de conexión con la API.');
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
});
