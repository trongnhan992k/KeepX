/* KeepX/static/js/app.js */

/**
 * 1. THEME APP
 * Quản lý Dark Mode toàn trang
 */
function themeApp() {
    return {
        darkMode: localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches),
        
        toggleTheme() {
            this.darkMode = !this.darkMode;
            localStorage.setItem('theme', this.darkMode ? 'dark' : 'light');
            if (this.darkMode) document.documentElement.classList.add('dark');
            else document.documentElement.classList.remove('dark');
        }
    };
}

/**
 * 2. NOTE APP
 * Quản lý logic trang danh sách ghi chú
 */
function noteApp(config) {
    return {
        // Cấu hình từ Template
        csrfToken: config.csrfToken,
        urls: {
            create: config.createUrl,
            update: config.updateUrl
        },

        // Data Models
        colors: [
            { bg: "#ffadad" }, { bg: "#ffd6a5" }, { bg: "#fdffb6" }, { bg: "#caffbf" },
            { bg: "#9bf6ff" }, { bg: "#a0c4ff" }, { bg: "#bdb2ff" }, { bg: "#ffc6ff" },
            { bg: "#e5e7eb" }, { bg: "" }
        ],
        
        // UI States
        isFormOpen: false,
        showFormatTools: false, // Trạng thái hiển thị thanh định dạng
        searchQuery: "",
        viewMode: localStorage.getItem('viewMode') || 'grid',
        isSaving: false,
        
        // Form Data
        currentNoteId: null,
        title: "",
        content: "",
        noteColor: "",
        isPinned: false,
        imageFile: null,
        imagePreview: null,
        tags: [],
        newTag: "",
        reminderTime: "",
        sharedEmails: "",
        
        // Checkbox Mode
        isCheckboxMode: false,
        checkboxes: [], 

        clientNotes: [],
        _timer: null,

        init() {
            this.$watch('title', () => this.debouncedSave());
            this.$watch('content', () => this.debouncedSave());
            
            // Watch checkboxes change để cập nhật content ẩn
            this.$watch('checkboxes', () => {
                if (this.isCheckboxMode) this.syncCheckboxToContent();
                this.debouncedSave();
            }, { deep: true });

            this.$watch('viewMode', (val) => localStorage.setItem('viewMode', val));
        },

        // FEATURE: FORMATTING
        execCmd(command) {
            document.execCommand(command, false, null);
            const editor = document.getElementById("editor");
            if (editor) this.content = editor.innerHTML;
        },

        // FEATURE: CHECKBOX LOGIC
        toggleCheckboxMode() {
            this.isCheckboxMode = !this.isCheckboxMode;
            if (this.isCheckboxMode) {
                // Chuyển HTML -> Mảng Checkbox
                let text = this.content
                    .replace(/<div>/g, "\n")
                    .replace(/<\/div>/g, "")
                    .replace(/<br>/g, "\n")
                    .replace(/&nbsp;/g, " ");
                
                let tmp = document.createElement("DIV");
                tmp.innerHTML = text;
                text = tmp.textContent || tmp.innerText || "";
                
                let lines = text.split("\n").filter(line => line.trim() !== "");
                this.checkboxes = lines.length > 0 
                    ? lines.map(line => ({ text: line, checked: false }))
                    : [{ text: "", checked: false }];
                
                this.syncCheckboxToContent();
            } else {
                // Chuyển Mảng Checkbox -> HTML
                this.content = this.checkboxes.map(item => `<div>${item.text}</div>`).join("");
                
                this.$nextTick(() => {
                    const editor = document.getElementById("editor");
                    if (editor) editor.innerHTML = this.content;
                });
            }
        },

        addCheckbox(index = null) {
            if (index !== null) {
                this.checkboxes.splice(index, 0, { text: "", checked: false });
                this.$nextTick(() => {
                    const inputs = this.$el.querySelectorAll("input[type='text']");
                    if (inputs[index]) inputs[index].focus();
                });
            } else {
                this.checkboxes.push({ text: "", checked: false });
            }
        },

        removeCheckbox(index) {
            if (this.checkboxes[index].text === "" && this.checkboxes.length > 1) {
                this.checkboxes.splice(index, 1);
                this.$nextTick(() => {
                    const inputs = this.$el.querySelectorAll("input[type='text']");
                    if (inputs[index - 1]) inputs[index - 1].focus();
                });
            }
        },

        syncCheckboxToContent() {
            this.content = JSON.stringify({ type: 'checklist', data: this.checkboxes });
        },

        // Helper mở nhanh từ trạng thái đóng
        quickAddImage() {
            this.openForm();
            setTimeout(() => this.$refs.fileInput.click(), 200);
        },
        
        quickAddChecklist() {
            this.openForm();
            this.isCheckboxMode = true;
            this.checkboxes = [{ text: "", checked: false }];
        },

        openForm() {
            this.isFormOpen = true;
            this.showFormatTools = false; // Luôn ẩn thanh format khi mới mở
            setTimeout(() => { 
                if (!this.imageFile && !this.currentNoteId) {
                    const titleInput = this.$el.querySelector("input[placeholder='Tiêu đề']");
                    if(titleInput) titleInput.focus();
                }
            }, 100);
        },

        debouncedSave() {
            if (this.currentNoteId && this.isFormOpen) {
                clearTimeout(this._timer);
                this.isSaving = true;
                this._timer = setTimeout(() => { this.saveNoteToDB(true); }, 1500);
            }
        },

        formatDate(isoString) {
            if(!isoString) return "";
            const date = new Date(isoString);
            return date.toLocaleString('vi-VN', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit'});
        },
        
        truncate(str, n){
            return (str && str.length > n) ? str.substr(0, n-1) + '...' : str;
        },

        editNote(note) {
            this.currentNoteId = note.id;
            this.title = note.title;
            this.noteColor = note.color;
            this.isPinned = note.is_pinned;
            this.tags = [...(note.labels || [])];
            this.imagePreview = note.image_url || null;
            this.reminderTime = note.reminder_time || "";
            this.sharedEmails = ""; 
            
            // Xử lý content (JSON checklist hoặc HTML)
            try {
                const parsed = JSON.parse(note.content);
                if (parsed && parsed.type === 'checklist') {
                    this.isCheckboxMode = true;
                    this.checkboxes = parsed.data;
                    this.content = note.content;
                } else {
                    throw new Error("Not checklist");
                }
            } catch (e) {
                this.isCheckboxMode = false;
                this.content = note.content;
                this.$nextTick(() => {
                    const editor = document.getElementById("editor");
                    if(editor) editor.innerHTML = this.content;
                });
            }
            
            this.openForm();
        },

        addTag() {
            const tag = this.newTag.trim();
            if (tag && !this.tags.includes(tag)) this.tags.push(tag);
            this.newTag = "";
        },
        
        removeTag(index) { this.tags.splice(index, 1); },
        
        handleFileUpload(event) {
            const file = event.target.files[0];
            if (file) {
                this.imageFile = file;
                this.imagePreview = URL.createObjectURL(file);
                this.openForm();
            }
        },
        
        removeImage() {
            this.imageFile = null;
            this.imagePreview = null;
            const fileInput = this.$refs.fileInput;
            if(fileInput) fileInput.value = "";
        },
        
        closeForm() {
            if (this.isSaving) {
                this.saveNoteToDB(false);
            } else if (!this.currentNoteId && (this.title.trim() || this.content.trim())) {
                this.saveNoteToDB(false);
            } else {
                this.isFormOpen = false;
                this.resetForm();
            }
        },

        async saveNoteToDB(silent = false) {
            const isUpdate = !!this.currentNoteId;
            const formData = new FormData();
            formData.append("title", this.title);
            formData.append("content", this.content);
            formData.append("color", this.noteColor);
            formData.append("is_pinned", this.isPinned ? "true" : "false");
            formData.append("labels", JSON.stringify(this.tags));
            formData.append("reminder", this.reminderTime);
            formData.append("shared_emails", this.sharedEmails);

            if (this.imageFile) formData.append("image", this.imageFile);
            formData.append("csrfmiddlewaretoken", this.csrfToken);

            let url = this.urls.create;
            if (isUpdate) {
                url = this.urls.update.replace("00000", this.currentNoteId);
            }

            try {
                const response = await fetch(url, { method: "POST", body: formData });
                if (response.ok) {
                    this.isSaving = false;
                    if (!silent) window.location.reload();
                }
            } catch (error) {
                console.error("Save error", error);
                this.isSaving = false;
            }
        },

        async updatePin(noteId, newStatus) {
            if (!noteId || noteId.length < 5) return;
            let finalUrl = this.urls.update.replace("00000", noteId);
            const formData = new FormData();
            formData.append("is_pinned", newStatus ? "true" : "false");
            formData.append("csrfmiddlewaretoken", this.csrfToken);
            fetch(finalUrl, { method: "POST", body: formData });
        },

        resetForm() {
            this.currentNoteId = null;
            this.title = "";
            this.content = "";
            const editor = document.getElementById("editor");
            if(editor) editor.innerHTML = "";
            this.noteColor = "";
            this.isPinned = false;
            this.tags = [];
            this.newTag = "";
            this.reminderTime = "";
            this.sharedEmails = "";
            this.isCheckboxMode = false;
            this.checkboxes = [];
            this.showFormatTools = false;
            this.removeImage();
            this.isSaving = false;
            clearTimeout(this._timer);
        },
    };
}