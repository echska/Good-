// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('documentForm');
    const statusDiv = document.getElementById('status');
    const statusMessage = document.getElementById('statusMessage');

    // Set default date and time to current
    const now = new Date();
    document.getElementById('docDate').valueAsDate = now;
    document.getElementById('docTime').value = now.toTimeString().slice(0, 5);

    // Company search functionality
    let companies = [];
    const companySearch = document.getElementById('companySearch');
    const companyResults = document.getElementById('companyResults');

    // Load companies data
    fetch('/companies')
        .then(res => res.json())
        .then(data => {
            companies = data;
            console.log('Loaded', companies.length, 'companies');
        })
        .catch(err => console.error('Failed to load companies:', err));

    // Search companies as user types
    companySearch.addEventListener('input', function() {
        const query = this.value.trim().toLowerCase();
        if (query.length < 1) {
            companyResults.style.display = 'none';
            return;
        }

        // Filter companies by number, name, or brand
        const filtered = companies.filter(c => {
            const num = String(c.Number);
            const name = (c.CompanyNameProject || '').toLowerCase();
            const brand = (c.Brand || '').toLowerCase();
            const license = String(c.LicenseApprovalNumber || '');
            return num.includes(query) || name.includes(query) || brand.includes(query) || license.includes(query);
        }).slice(0, 15); // Limit to 15 results

        if (filtered.length === 0) {
            companyResults.innerHTML = '<div class="search-result-item">لا توجد نتائج</div>';
        } else {
            companyResults.innerHTML = filtered.map(c => `
                <div class="search-result-item" data-id="${c.Number}">
                    <span class="company-number">${c.Number}</span>
                    <span class="company-name">${c.CompanyNameProject}</span>
                    <span class="company-brand">${c.Brand}</span>
                </div>
            `).join('');

            // Add click handlers
            companyResults.querySelectorAll('.search-result-item[data-id]').forEach(item => {
                item.addEventListener('click', function() {
                    const companyId = parseInt(this.dataset.id);
                    const company = companies.find(c => c.Number === companyId);
                    if (company) {
                        fillCompanyData(company);
                        companyResults.style.display = 'none';
                        companySearch.value = `${company.Number} - ${company.CompanyNameProject}`;
                    }
                });
            });
        }
        companyResults.style.display = 'block';
    });

    // Hide results when clicking outside
    document.addEventListener('click', function(e) {
        if (!companySearch.contains(e.target) && !companyResults.contains(e.target)) {
            companyResults.style.display = 'none';
        }
    });

    // Fill form with company data
    function fillCompanyData(company) {
        // Auto-fill fields - user can still edit
        if (company.CompanyNameProject) {
            document.getElementById('companyName').value = company.CompanyNameProject;
        }
        if (company.Brand) {
            document.getElementById('companyBrand').value = company.Brand;
            document.getElementById('trademark').value = company.Brand;
        }
        if (company.GovernorateName) {
            // Try to select matching province
            const provinceSelect = document.getElementById('provinceName');
            for (let option of provinceSelect.options) {
                if (option.value === company.GovernorateName || option.text === company.GovernorateName) {
                    provinceSelect.value = option.value;
                    break;
                }
            }
        }
        if (company.LicenseApprovalNumber) {
            document.getElementById('licenseNumber').value = company.LicenseApprovalNumber;
        }
        if (company.GrantingLicenseApproval) {
            document.getElementById('licenseAuthority').value = company.GrantingLicenseApproval;
        }
        if (company.LicenseApprovalDate) {
            document.getElementById('licenseDate').value = company.LicenseApprovalDate;
        }
        if (company.LicenseTextSpecialization) {
            document.getElementById('licenseDescription').value = company.LicenseTextSpecialization;
            document.getElementById('cargoType').value = company.LicenseTextSpecialization;
        }
        if (company.TypeIndustryProduction) {
            document.getElementById('licensedProducts').value = company.TypeIndustryProduction;
            document.getElementById('productType').value = company.TypeIndustryProduction;
        }
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Form submitted!');
        await generateDocument();
    });

    async function generateDocument() {
        console.log('generateDocument called');
        // Get form values
        const formData = {
            docNumber: document.getElementById('docNumber').value,
            docDate: document.getElementById('docDate').value,
            docTime: document.getElementById('docTime').value,
            entryPoint: document.getElementById('entryPoint').value,
            driverName: document.getElementById('driverName').value,
            vehicleNumber: document.getElementById('vehicleNumber').value,
            vehicleProvince: document.getElementById('vehicleProvince').value,
            weight: document.getElementById('weight').value,
            destination: document.getElementById('destination').value,
            companyName: document.getElementById('companyName').value,
            cargoType: document.getElementById('cargoType').value,
            provinceName: document.getElementById('provinceName').value,
            licenseAuthority: document.getElementById('licenseAuthority').value,
            licenseNumber: document.getElementById('licenseNumber').value,
            licenseDate: document.getElementById('licenseDate').value,
            licenseDescription: document.getElementById('licenseDescription').value,
            trademark: document.getElementById('trademark').value,
            licensedProducts: document.getElementById('licensedProducts').value,
            companyBrand: document.getElementById('companyBrand').value,
            productType: document.getElementById('productType').value,
            productWeight: document.getElementById('productWeight').value
        };

        // Handle QR code file upload
        const qrFile = document.getElementById('qrFile').files[0];
        if (qrFile) {
            // Convert uploaded image to base64
            const qrBase64 = await new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = (e) => resolve(e.target.result);
                reader.readAsDataURL(qrFile);
            });
            formData.qrImage = qrBase64;
        }

        // Format date (DD-MM-YYYY)
        const dateObj = new Date(formData.docDate);
        formData.docDate = `${dateObj.getDate().toString().padStart(2, '0')}-${(dateObj.getMonth() + 1).toString().padStart(2, '0')}-${dateObj.getFullYear()}`;

        // Format time with AM/PM
        const timeParts = formData.docTime.split(':');
        let hours = parseInt(timeParts[0]);
        const minutes = timeParts[1];
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12 || 12; // Convert to 12-hour format
        formData.docTime = `${hours}:${minutes} ${ampm}`;

        // Show loading status
        const submitBtn = document.querySelector('.submit-btn');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'جاري إنشاء PDF...';
        submitBtn.disabled = true;

        showStatus('جاري إنشاء الوثيقة...', 'info');

        try {
            // Send request to backend (works with any domain)
            console.log('Sending data to server:', formData);
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            console.log('Response received:', response);

            if (!response.ok) {
                throw new Error('فشل في إنشاء الوثيقة');
            }

            // Get the PDF/DOCX blob
            const blob = await response.blob();

            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            // Determine file extension from content type
            const contentType = response.headers.get('content-type');
            const extension = contentType.includes('pdf') ? 'pdf' : 'docx';

            a.download = `وثيقة-${formData.docNumber}.${extension}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showStatus('تم إنشاء الوثيقة بنجاح! ✓', 'success');

        } catch (error) {
            console.error('Error generating document:', error);
            console.error('Error stack:', error.stack);
            showStatus(`حدث خطأ: ${error.message}`, 'error');
        } finally {
            // Reset button
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusDiv.style.display = 'block';

        // Set colors based on type
        if (type === 'success') {
            statusDiv.style.backgroundColor = '#d4edda';
            statusDiv.style.color = '#155724';
            statusDiv.style.border = '1px solid #c3e6cb';
        } else if (type === 'error') {
            statusDiv.style.backgroundColor = '#f8d7da';
            statusDiv.style.color = '#721c24';
            statusDiv.style.border = '1px solid #f5c6cb';
        } else {
            statusDiv.style.backgroundColor = '#d1ecf1';
            statusDiv.style.color = '#0c5460';
            statusDiv.style.border = '1px solid #bee5eb';
        }

        // Auto-hide after 5 seconds for success/info
        if (type !== 'error') {
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 5000);
        }
    }
});
