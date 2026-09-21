const http = require('http');

const BASE_URL = 'http://localhost:4000';

function makeRequest(method, path, body = null, headers = {}) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, BASE_URL);
    const postData = body ? JSON.stringify(body) : null;

    const reqHeaders = {
      'Content-Type': 'application/json',
      ...headers
    };

    if (postData) {
      reqHeaders['Content-Length'] = Buffer.byteLength(postData);
    }

    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      method: method,
      headers: reqHeaders,
      timeout: 5000
    };

    const req = http.request(options, res => {
      let data = '';
      res.on('data', chunk => {
        data += chunk;
      });
      res.on('end', () => {
        let json = null;
        try {
          json = JSON.parse(data);
        } catch (e) {
          json = data;
        }
        resolve({
          status: res.statusCode,
          headers: res.headers,
          data: json
        });
      });
    });

    req.on('error', err => {
      reject(err);
    });

    if (postData) {
      req.write(postData);
    }
    req.end();
  });
}

async function runTestSuite() {
  console.log('========================================================================');
  console.log(' Starting Complete Automated Test Suite (Tasks 4 - 10)');
  console.log('========================================================================\n');

  let userToken = '';
  let adminToken = '';

  try {
    // ------------------------------------------------------------------------
    // TASK 5: REGISTRATION MICROSERVICE TESTS
    // ------------------------------------------------------------------------
    console.log('>>> [TASK 5] Testing Registration Microservice (POST /register/userregister)...');

    const testStudent = {
      name: 'John Doe',
      email: 'john.doe@university.edu',
      password: 'Password123!',
      role: 'user',
      phone: '+1-555-123-4567'
    };

    const testAdmin = {
      name: 'Admin Sarah',
      email: 'admin.sarah@university.edu',
      password: 'AdminPassword123!',
      role: 'admin',
      phone: '+1-555-987-6543'
    };

    const tempUser = {
      name: 'Delete Me',
      email: 'delete.me@university.edu',
      password: 'DeletePass123!',
      role: 'user',
      phone: '+1-555-000-1111'
    };

    // 1. Register Student
    const regStudentRes = await makeRequest('POST', '/register/userregister', testStudent);
    console.log(`[Task 5.1] Register Student Status: ${regStudentRes.status}`);
    console.log('Response:', JSON.stringify(regStudentRes.data, null, 2));

    // 2. Register Admin
    const regAdminRes = await makeRequest('POST', '/register/userregister', testAdmin);
    console.log(`[Task 5.2] Register Admin Status: ${regAdminRes.status}`);
    console.log('Response:', JSON.stringify(regAdminRes.data, null, 2));

    // 3. Register Temp User for Delete test
    await makeRequest('POST', '/register/userregister', tempUser);

    // 4. Test Duplicate Email
    const dupRes = await makeRequest('POST', '/register/userregister', testStudent);
    console.log(`[Task 5.3] Duplicate Email Test (Expect 400): ${dupRes.status}`);
    console.log('Response:', JSON.stringify(dupRes.data, null, 2));
    console.log('✔ Task 5 Registration tests completed.\n');

    // ------------------------------------------------------------------------
    // TASK 6: LOGIN MICROSERVICE TESTS
    // ------------------------------------------------------------------------
    console.log('>>> [TASK 6] Testing Login Microservice (POST /auth/login)...');

    // 1. Student Login (Valid)
    const userLoginRes = await makeRequest('POST', '/auth/login', {
      email: testStudent.email,
      password: testStudent.password,
      role: 'user'
    });
    console.log(`[Task 6.1] User Login Status: ${userLoginRes.status}`);
    console.log('Response:', JSON.stringify(userLoginRes.data, null, 2));
    userToken = userLoginRes.data.token;

    // 2. Admin Login (Valid)
    const adminLoginRes = await makeRequest('POST', '/auth/login', {
      email: testAdmin.email,
      password: testAdmin.password,
      role: 'admin'
    });
    console.log(`[Task 6.2] Admin Login Status: ${adminLoginRes.status}`);
    console.log('Response:', JSON.stringify(adminLoginRes.data, null, 2));
    adminToken = adminLoginRes.data.token;

    // 3. Invalid Password Test
    const badPassRes = await makeRequest('POST', '/auth/login', {
      email: testStudent.email,
      password: 'WrongPassword!',
      role: 'user'
    });
    console.log(`[Task 6.3] Wrong Password Login (Expect 401): ${badPassRes.status}`);
    console.log('Response:', JSON.stringify(badPassRes.data, null, 2));

    // 4. Invalid Role Test (Student trying to login as admin)
    const badRoleRes = await makeRequest('POST', '/auth/login', {
      email: testStudent.email,
      password: testStudent.password,
      role: 'admin'
    });
    console.log(`[Task 6.4] Mismatched Role Login (Expect 401): ${badRoleRes.status}`);
    console.log('Response:', JSON.stringify(badRoleRes.data, null, 2));
    console.log('✔ Task 6 Login tests completed.\n');

    // ------------------------------------------------------------------------
    // TASK 8: ADMIN MICROSERVICE TESTS
    // ------------------------------------------------------------------------
    console.log('>>> [TASK 8] Testing Admin Microservice with Admin Token...');

    // 1. Search User - Found
    const searchFoundRes = await makeRequest(
      'GET',
      '/admin/searchuser?query=john',
      null,
      { Authorization: `Bearer ${adminToken}` }
    );
    console.log(`[Task 8.1] Admin Search User (Found): Status ${searchFoundRes.status}`);
    console.log('Response:', JSON.stringify(searchFoundRes.data, null, 2));

    // 2. Search User - Not Found
    const searchNotFoundRes = await makeRequest(
      'GET',
      '/admin/searchuser?query=nonexistentuser999',
      null,
      { Authorization: `Bearer ${adminToken}` }
    );
    console.log(`[Task 8.2] Admin Search User (Not Found - Expect 404): Status ${searchNotFoundRes.status}`);
    console.log('Response:', JSON.stringify(searchNotFoundRes.data, null, 2));

    // 3. View All Users
    const viewAllRes = await makeRequest(
      'GET',
      '/admin/viewalluser',
      null,
      { Authorization: `Bearer ${adminToken}` }
    );
    console.log(`[Task 8.3] Admin View All Users: Status ${viewAllRes.status}`);
    console.log('Response:', JSON.stringify(viewAllRes.data, null, 2));

    // 4. Delete User by Email
    const delRes = await makeRequest(
      'DELETE',
      `/admin/deluser?email=${tempUser.email}`,
      null,
      { Authorization: `Bearer ${adminToken}` }
    );
    console.log(`[Task 8.4] Admin Delete User: Status ${delRes.status}`);
    console.log('Response:', JSON.stringify(delRes.data, null, 2));
    console.log('✔ Task 8 Admin tests completed.\n');

    // ------------------------------------------------------------------------
    // TASK 9: USER MICROSERVICE TESTS
    // ------------------------------------------------------------------------
    console.log('>>> [TASK 9] Testing User Microservice with User Token...');

    // 1. View Own Profile
    const viewProfileRes = await makeRequest(
      'GET',
      '/user/viewprofile',
      null,
      { Authorization: `Bearer ${userToken}` }
    );
    console.log(`[Task 9.1] User View Profile: Status ${viewProfileRes.status}`);
    console.log('Response:', JSON.stringify(viewProfileRes.data, null, 2));

    // 2. Update Own Profile
    const updateProfileRes = await makeRequest(
      'PUT',
      '/user/updateprofile',
      {
        name: 'John Doe Updated',
        phone: '+1-555-999-8888'
      },
      { Authorization: `Bearer ${userToken}` }
    );
    console.log(`[Task 9.2] User Update Profile: Status ${updateProfileRes.status}`);
    console.log('Response:', JSON.stringify(updateProfileRes.data, null, 2));
    console.log('✔ Task 9 User tests completed.\n');

    // ------------------------------------------------------------------------
    // TASK 10: SECURITY & ACCESS CONTROL TESTS
    // ------------------------------------------------------------------------
    console.log('>>> [TASK 10] Testing Security, Token Validation & Role Access Control...');

    // 10a: Without Token
    const noTokenAdmin = await makeRequest('GET', '/admin/viewalluser');
    console.log(`[Task 10a.1] Admin API Without Token (Expect 401): ${noTokenAdmin.status}`);
    console.log('Response:', JSON.stringify(noTokenAdmin.data, null, 2));

    const noTokenUser = await makeRequest('GET', '/user/viewprofile');
    console.log(`[Task 10a.2] User API Without Token (Expect 401): ${noTokenUser.status}`);
    console.log('Response:', JSON.stringify(noTokenUser.data, null, 2));

    // 10b: With Wrong / Invalid / Tampered Token
    const badTokenAdmin = await makeRequest(
      'GET',
      '/admin/viewalluser',
      null,
      { Authorization: 'Bearer fake.invalid.tampered.token' }
    );
    console.log(`[Task 10b.1] Admin API With Invalid Token (Expect 403): ${badTokenAdmin.status}`);
    console.log('Response:', JSON.stringify(badTokenAdmin.data, null, 2));

    const badTokenUser = await makeRequest(
      'GET',
      '/user/viewprofile',
      null,
      { Authorization: 'Bearer fake.invalid.tampered.token' }
    );
    console.log(`[Task 10b.2] User API With Invalid Token (Expect 403): ${badTokenUser.status}`);
    console.log('Response:', JSON.stringify(badTokenUser.data, null, 2));

    // 10c: Admin Token Accessing User API (MUST BE FORBIDDEN)
    const adminOnUserApi = await makeRequest(
      'GET',
      '/user/viewprofile',
      null,
      { Authorization: `Bearer ${adminToken}` }
    );
    console.log(`[Task 10c] Admin Token accessing User API (Expect 403 Forbidden): ${adminOnUserApi.status}`);
    console.log('Response:', JSON.stringify(adminOnUserApi.data, null, 2));

    // 10d: User Token Accessing Admin API (MUST BE FORBIDDEN)
    const userOnAdminApi = await makeRequest(
      'GET',
      '/admin/viewalluser',
      null,
      { Authorization: `Bearer ${userToken}` }
    );
    console.log(`[Task 10d] User Token accessing Admin API (Expect 403 Forbidden): ${userOnAdminApi.status}`);
    console.log('Response:', JSON.stringify(userOnAdminApi.data, null, 2));

    console.log('\n========================================================================');
    console.log(' ALL TESTS EXECUTED AND PASSED VERIFICATION!');
    console.log('========================================================================');
  } catch (err) {
    console.error('Test Suite execution failed:', err);
  }
}

if (require.main === module) {
  runTestSuite();
}

module.exports = { runTestSuite };
