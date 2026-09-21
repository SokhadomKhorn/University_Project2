const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');

// 1. Mongoose Schema Definition (Task 3 Specification)
const userSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: [true, 'Name is required'],
      trim: true
    },
    email: {
      type: String,
      required: [true, 'Email is required'],
      unique: true,
      lowercase: true,
      trim: true
    },
    password: {
      type: String,
      required: [true, 'Password is required']
    },
    role: {
      type: String,
      required: [true, 'Role is required'],
      enum: ['admin', 'user'],
      default: 'user'
    },
    phone: {
      type: String,
      required: [true, 'Phone number is required'],
      trim: true
    }
  },
  {
    timestamps: true
  }
);

const MongooseModel = mongoose.models.User || mongoose.model('User', userSchema);

// Shared File Store for offline fallback
const DATA_DIR = path.resolve(__dirname, '..', '..', '.data');
const DATA_FILE = path.join(DATA_DIR, 'users.json');

const readStore = () => {
  try {
    if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
    if (!fs.existsSync(DATA_FILE)) {
      fs.writeFileSync(DATA_FILE, JSON.stringify([]));
      return [];
    }
    return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8') || '[]');
  } catch (e) {
    return [];
  }
};

const writeStore = (data) => {
  try {
    if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf8');
  } catch (e) {}
};

const sanitizeDoc = (obj) => {
  if (!obj) return null;
  const raw = obj._doc ? { ...obj._doc } : { ...obj };
  delete raw.password;
  delete raw._doc;
  return raw;
};

class QueryChain {
  constructor(resolver) {
    this._resolver = resolver;
    this._excludePassword = false;
    this._sortCriteria = null;
  }

  select(fields) {
    if (fields === '-password') this._excludePassword = true;
    return this;
  }

  sort(criteria) {
    this._sortCriteria = criteria;
    return this;
  }

  async exec() {
    let res = await Promise.resolve(this._resolver());
    if (!res) return null;
    if (Array.isArray(res)) {
      let result = [...res];
      if (this._sortCriteria && this._sortCriteria.createdAt === -1) {
        result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
      }
      return this._excludePassword ? result.map(u => sanitizeDoc(u)) : result;
    } else {
      return this._excludePassword ? sanitizeDoc(res) : (res._doc ? { ...res._doc } : { ...res });
    }
  }

  then(resolve, reject) {
    return this.exec().then(resolve, reject);
  }

  catch(reject) {
    return this.exec().catch(reject);
  }
}

class UserAdapter {
  constructor(data) {
    if (mongoose.connection && mongoose.connection.readyState === 1) {
      return new MongooseModel(data);
    }
    this._doc = {
      _id: new mongoose.Types.ObjectId().toString(),
      name: data.name,
      email: data.email ? data.email.toLowerCase().trim() : '',
      password: data.password,
      role: data.role || 'user',
      phone: data.phone,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    Object.assign(this, this._doc);
  }

  async save() {
    if (mongoose.connection && mongoose.connection.readyState === 1) {
      const doc = new MongooseModel(this);
      return await doc.save();
    }
    const store = readStore();
    const existing = store.find(u => u.email === this.email.toLowerCase().trim());
    if (existing) {
      const err = new Error('Duplicate key error');
      err.code = 11000;
      throw err;
    }
    this.createdAt = new Date().toISOString();
    this.updatedAt = new Date().toISOString();
    this._doc.createdAt = this.createdAt;
    this._doc.updatedAt = this.updatedAt;
    store.push({ ...this._doc });
    writeStore(store);
    return this._doc;
  }

  static findOne(query) {
    if (mongoose.connection && mongoose.connection.readyState === 1) {
      return MongooseModel.findOne(query);
    }
    return new QueryChain(() => {
      const store = readStore();
      return query._id
        ? store.find(u => u._id === query._id.toString())
        : store.find(u => u.email === query.email.toLowerCase().trim());
    });
  }

  static find(filter = {}) {
    if (mongoose.connection && mongoose.connection.readyState === 1) {
      return MongooseModel.find(filter);
    }
    return new QueryChain(() => {
      let list = readStore();
      if (filter.$or) {
        list = list.filter(u =>
          filter.$or.some(cond => {
            if (cond.email && u.email.toLowerCase() === cond.email.toLowerCase()) return true;
            if (cond.name && cond.name.$regex) {
              return new RegExp(cond.name.$regex, cond.name.$options || 'i').test(u.name);
            }
            if (cond.email && cond.email.$regex) {
              return new RegExp(cond.email.$regex, cond.email.$options || 'i').test(u.email);
            }
            return false;
          })
        );
      } else if (filter.email) {
        list = list.filter(u => u.email === filter.email.toLowerCase());
      } else if (filter.name) {
        const reg = filter.name.$regex ? new RegExp(filter.name.$regex, filter.name.$options || 'i') : null;
        list = list.filter(u => (reg ? reg.test(u.name) : u.name.toLowerCase().includes(filter.name.toLowerCase())));
      }
      return list;
    });
  }

  static findById(id) {
    if (mongoose.connection && mongoose.connection.readyState === 1) {
      return MongooseModel.findById(id);
    }
    return this.findOne({ _id: id });
  }

  static findOneAndDelete(query) {
    if (mongoose.connection && mongoose.connection.readyState === 1) {
      return MongooseModel.findOneAndDelete(query);
    }
    return new QueryChain(() => {
      const store = readStore();
      const idx = store.findIndex(u =>
        query.email ? u.email === query.email.toLowerCase().trim() : u._id === query._id.toString()
      );
      if (idx === -1) return null;
      const deleted = store.splice(idx, 1)[0];
      writeStore(store);
      return deleted;
    });
  }

  static findAndUpdate(query, update, options = {}) {
    return this.findOneAndUpdate(query, update, options);
  }

  static findOneAndUpdate(query, update, options = {}) {
    if (mongoose.connection && mongoose.connection.readyState === 1) {
      return MongooseModel.findOneAndUpdate(query, update, options);
    }
    return new QueryChain(() => {
      const store = readStore();
      const user = store.find(u =>
        query._id ? u._id === query._id.toString() : u.email === query.email.toLowerCase().trim()
      );
      if (!user) return null;
      if (update.$set) Object.assign(user, update.$set);
      user.updatedAt = new Date().toISOString();
      writeStore(store);
      return user;
    });
  }
}

module.exports = UserAdapter;
