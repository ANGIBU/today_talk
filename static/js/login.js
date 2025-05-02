document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginButton = document.getElementById('loginButton');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const signupPanel = document.getElementById('signupPanel');
    const signupForm = document.getElementById('signupForm');
 
    function validateInput(input, minLength, maxLength, type) {
        const value = input.value.trim();
        const isEmpty = value.length === 0;
        const isValidLength = value.length >= minLength && value.length <= maxLength;
        const isValidEmail = type === 'email' ? /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) : true;

        const validationContainer = input.parentElement.querySelector('.validation-container');
        const hint = validationContainer.querySelector('.form-hint');
        const error = validationContainer.querySelector('.error-message');
        
        // 빈 값 체크
        if (isEmpty) {
            updateUI(input, hint, error, 'default', 
                `! ${type === 'email' ? '이메일을 입력하세요' : '입력해주세요'}`, 
                '');
            return;
        }

        // 길이/형식 체크
        if (!isValidLength || (type === 'email' && !isValidEmail)) {
            updateUI(input, hint, error, 'invalid', 
                `✗ ${type === 'nickname' ? '3~8자리로 입력해주세요' : 
                     type === 'username' ? '4~16자리로 입력해주세요' : 
                     type === 'email' ? '올바른 이메일 형식이 아닙니다' : 
                     '8~20자리로 입력해주세요'}`, 
                '');
            return;
        }

        // 중복 체크
        checkDuplicate(input, type);
    }
 
    function updateUI(input, hint, error, status, hintText, errorText) {
        hint.textContent = hintText;
        hint.className = `form-hint ${status}`;
        input.classList.remove('valid', 'invalid');
        if (status !== 'default') {
            input.classList.add(status);
        }
    }
 
    async function checkDuplicate(input, type) {
        const endpoints = {
            'nickname': '/check-nickname',
            'username': '/check-id',
            'email': '/check-email'
        };

        const displayNames = {
            'nickname': '닉네임',
            'username': '아이디',
            'email': '이메일'
        };

        const requestData = { [type]: input.value.trim() };

        try {
            const response = await fetch(endpoints[type], {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();
            const validationContainer = input.parentElement.querySelector('.validation-container');
            const hint = validationContainer.querySelector('.form-hint');
            
            if (data.is_duplicate) {
                // 중복된 경우
                updateUI(input, hint, null, 'invalid', 
                    `✗ 중복된 ${displayNames[type]}입니다`, 
                    '');
            } else {
                // 모든 조건 통과
                updateUI(input, hint, null, 'valid', 
                    `✓ 사용 가능한 ${displayNames[type]}`, 
                    '');
            }
        } catch (error) {
            console.error(error);
            const validationContainer = input.parentElement.querySelector('.validation-container');
            const hint = validationContainer.querySelector('.form-hint');
            updateUI(input, hint, null, 'invalid', 
                '✗ 서버 오류', 
                '');
        }
    }
 
    function validatePasswordMatch(input) {
        const password = document.getElementById('signup-password').value;
        const isValid = input.value === password;
        const validationContainer = input.parentElement.querySelector('.validation-container');
        const hint = validationContainer.querySelector('.form-hint');
 
        if (!input.value) {
            updateUI(input, hint, null, 'default',
                '! 비밀번호를 한번 더 입력해주세요', 
                '');
        } else {
            updateUI(input, hint, null,
                isValid ? 'valid' : 'invalid',
                isValid ? '✓ 비밀번호가 일치합니다' : '✗ 비밀번호가 일치하지 않습니다',
                '');
        }
    }
 
    function validateLoginForm() {
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();
        const isValid = username.length >= 4 && username.length <= 16 && 
                       password.length >= 8 && password.length <= 20;
        
        loginButton.disabled = !isValid;
        loginButton.classList.toggle('active', isValid);
    }
 
    document.getElementById('nickname').addEventListener('input', e => 
        validateInput(e.target, 3, 8, 'nickname'));
 
    document.getElementById('signup-username').addEventListener('input', e => 
        validateInput(e.target, 4, 16, 'username'));
 
    document.getElementById('signup-email').addEventListener('input', e => 
        validateInput(e.target, 5, 50, 'email'));
 
    document.getElementById('signup-password').addEventListener('input', e => {
        const input = e.target;
        const value = input.value.trim();
        const isValid = value.length >= 8 && value.length <= 20;
        const validationContainer = input.parentElement.querySelector('.validation-container');
        const hint = validationContainer.querySelector('.form-hint');
 
        updateUI(input, hint, null,
            !value ? 'default' : isValid ? 'valid' : 'invalid',
            !value ? '! 비밀번호를 입력해주세요' : 
                    isValid ? '✓ 8~20자 이내입니다' : '✗ 8~20자 이내여야 합니다',
            '');
        
        const confirmInput = document.getElementById('password-confirm');
        if (confirmInput.value) {
            validatePasswordMatch(confirmInput);
        }
    });
 
    document.getElementById('password-confirm').addEventListener('input', e => 
        validatePasswordMatch(e.target));
 
    usernameInput.addEventListener('input', validateLoginForm);
    passwordInput.addEventListener('input', validateLoginForm);
 
    document.getElementById('showSignup').addEventListener('click', e => {
        e.preventDefault();
        signupPanel.classList.add('show');
    });
 
    document.getElementById('closeSignup').addEventListener('click', () => 
        signupPanel.classList.remove('show'));
 
    signupForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const isValid = Array.from(this.elements).filter(el => 
            el.tagName === 'INPUT' && el.hasAttribute('required')
        ).every(element => 
            element.classList.contains('valid')
        );
        
        if (isValid) {
            this.submit();
        } else {
            alert('모든 항목을 올바르게 입력해주세요.');
        }
    });
});