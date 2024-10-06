document.addEventListener('DOMContentLoaded', function() {
    const jsonResponse = {
        "company_name": "AlphaArt",
        "industry": "Art Subscription Box",
        "recommendations": [
            {
                "accelerator": "Jumpstart Your Alteryx",
                "category": "Category_Business Intelligence and Analytics",
                "description": "Kickstart your adoption of Alteryx!"
            },
            {
                "accelerator": "Jumpstart Your QlikView",
                "category": "Category_Business Intelligence and Analytics",
                "description": "Kickstart your adoption of QlikView!"
            },
            {
                "accelerator": "Jumpstart Your Monday.com",
                "category": "Category_Project Management",
                "description": "Kickstart your adoption of Monday.com!"
            }
        ]
    };

    function createCard(accelerator) {
        return 
            <div class="card mb-3">
                <h3 class="card-header">${accelerator.accelerator}</h3>
                <div class="card-body">
                    <h5 class="card-title">${accelerator.category}</h5>
                    <p class="card-text">${accelerator.description}</p>
                </div>
            </div>
        ;
    }

    function displayGallery() {
        const gallery = document.getElementById('gallery-grid');
        jsonResponse.recommendations.forEach(accelerator => {
            gallery.innerHTML += createCard(accelerator);
        });
    }

    displayGallery();
});