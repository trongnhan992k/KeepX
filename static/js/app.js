/* KeepX/static/js/app.js */

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

function noteApp(config) {
    return {
        csrfToken: config.csrfToken,
        urls: {
            create: config.createUrl,
            update: config.updateUrl,
            delete: config.deleteUrl,
            bulk: config.bulkUrl || '/api/bulk-action/' // [MỚI] URL xử lý hàng loạt
        },

        colors: [
            { bg: "#ffadad" }, { bg: "#ffd6a5" }, { bg: "#fdffb6" }, { bg: "#caffbf" },
            { bg: "#9bf6ff" }, { bg: "#a0c4ff" }, { bg: "#bdb2ff" }, { bg: "#ffc6ff" },
            { bg: "#e5e7eb" }, { bg: "" }
        ],
        
        searchQuery: "",
        filterStatus: "all",
        viewMode: localStorage.getItem('viewMode') || 'grid',
        isSaving: false,
        
        // [MỚI] CHẾ ĐỘ CHỌN NHIỀU
        isSelectionMode: false,
        selectedIds: [],

        // Form Data
        isFormOpen: false,
        showFormatTools: false,
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
        deadline: "",
        status: "todo",
        
        isCheckboxMode: false,
        checkboxes: [], 
        _timer: null,

        init() {
            this.$watch('title', () => this.debouncedSave());
            this.$watch('content', () => this.debouncedSave());
            this.$watch('status', () => this.debouncedSave());
            this.$watch('deadline', () => this.debouncedSave());
            this.$watch('checkboxes', () => {
                if (this.isCheckboxMode) this.syncCheckboxToContent();
                this.debouncedSave();
            }, { deep: true });
            this.$watch('viewMode', (val) => localStorage.setItem('viewMode', val));
        },

        // --- [MỚI] LOGIC CHỌN NHIỀU ---
        toggleSelectionMode() {
            this.isSelectionMode = !this.isSelectionMode;
            this.selectedIds = []; // Reset khi tắt/bật
        },

        toggleNoteSelection(id) {
            if (this.selectedIds.includes(id)) {
                this.selectedIds = this.selectedIds.filter(itemId => itemId !== id);
            } else {
                this.selectedIds.push(id);
            }
        },

        selectAll() {
            // Lấy tất cả note visible trong DOM (đã lọc)
            const visibleNotes = Array.from(document.querySelectorAll('[data-note-id]'));
            const visibleIds = visibleNotes.map(el => el.getAttribute('data-note-id'));
            
            if (this.selectedIds.length === visibleIds.length) {
                this.selectedIds = []; // Bỏ chọn hết
            } else {
                this.selectedIds = visibleIds; // Chọn hết
            }
        },

        async performBulkAction(action) {
            if (this.selectedIds.length === 0) return;
            if (!confirm(`Bạn có chắc muốn thực hiện với ${this.selectedIds.length} mục đã chọn?`)) return;

            try {
                const response = await fetch(this.urls.bulk, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": this.csrfToken
                    },
                    body: JSON.stringify({
                        note_ids: this.selectedIds,
                        action: action
                    })
                });

                if (response.ok) {
                    window.location.reload();
                } else {
                    alert("Có lỗi xảy ra!");
                }
            } catch (e) {
                console.error("Bulk action failed", e);
                alert("Lỗi kết nối!");
            }
        },

        // --- Hàm sắp xếp cũ ---
        reorderNotes() {
            const container = document.getElementById('notes-container');
            if (!container) return;
            const items = Array.from(container.children);
            items.sort((a, b) => {
                const pinA = a.getAttribute('data-pinned') === 'true';
                const pinB = b.getAttribute('data-pinned') === 'true';
                if (pinA !== pinB) return pinB - pinA;
                const dateA = parseInt(a.getAttribute('data-created') || '0');
                const dateB = parseInt(b.getAttribute('data-created') || '0');
                return dateB - dateA;
            });
            items.forEach(item => container.appendChild(item));
        },

        async togglePin(noteId, currentPinState, element) {
            const newPinState = !currentPinState;
            const noteCard = element.closest('[data-pinned]');
            if (noteCard) {
                noteCard.setAttribute('data-pinned', newPinState ? 'true' : 'false');
                noteCard.style.transition = "transform 0.2s ease";
                noteCard.style.transform = "scale(0.98)";
                setTimeout(() => noteCard.style.transform = "scale(1)", 200);
            }
            await this.quickUpdate(noteId, { is_pinned: newPinState });
            setTimeout(() => { this.reorderNotes(); }, 300);
            return newPinState;
        },

        // --- QUICK ACTIONS ---
        async quickUpdate(noteId, data) {
            if (!noteId) return;
            const url = this.urls.update.replace("00000", noteId);
            const formData = new FormData();
            for (const key in data) {
                formData.append(key, data[key]);
            }
            formData.append("csrfmiddlewaretoken", this.csrfToken);
            try { await fetch(url, { method: "POST", body: formData }); } 
            catch (e) { console.error("Quick update failed", e); }
        },

        async quickUploadImage(noteId, file) {
            if (!noteId || !file) return;
            const url = this.urls.update.replace("00000", noteId);
            const formData = new FormData();
            formData.append("image", file);
            formData.append("csrfmiddlewaretoken", this.csrfToken);
            try { await fetch(url, { method: "POST", body: formData }); } 
            catch (e) { console.error("Quick upload failed", e); }
        },
        
        execCmd(command) {
            document.execCommand(command, false, null);
            const editor = document.getElementById("editor");
            if (editor) this.content = editor.innerHTML;
        },

        toggleCheckboxMode() {
            this.isCheckboxMode = !this.isCheckboxMode;
            if (this.isCheckboxMode) {
                let text = this.content.replace(/<div>/g, "\n").replace(/<\/div>/g, "").replace(/<br>/g, "\n").replace(/&nbsp;/g, " ");
                let tmp = document.createElement("DIV"); tmp.innerHTML = text;
                text = tmp.textContent || tmp.innerText || "";
                let lines = text.split("\n").filter(line => line.trim() !== "");
                this.checkboxes = lines.length > 0 ? lines.map(line => ({ text: line, checked: false })) : [{ text: "", checked: false }];
                this.syncCheckboxToContent();
            } else {
                this.content = this.checkboxes.map(item => `<div>${item.text}</div>`).join("");
                this.$nextTick(() => { const editor = document.getElementById("editor"); if (editor) editor.innerHTML = this.content; });
            }
        },

        addCheckbox(index = null) {
            if (index !== null) {
                this.checkboxes.splice(index, 0, { text: "", checked: false });
                this.$nextTick(() => { const inputs = this.$el.querySelectorAll("input[type='text']"); if (inputs[index]) inputs[index].focus(); });
            } else { this.checkboxes.push({ text: "", checked: false }); }
        },

        removeCheckbox(index) {
            if (this.checkboxes[index].text === "" && this.checkboxes.length > 1) {
                this.checkboxes.splice(index, 1);
                this.$nextTick(() => { const inputs = this.$el.querySelectorAll("input[type='text']"); if (inputs[index - 1]) inputs[index - 1].focus(); });
            }
        },

        syncCheckboxToContent() { this.content = JSON.stringify({ type: 'checklist', data: this.checkboxes }); },

        quickAddImage() { this.openForm(); setTimeout(() => this.$refs.fileInput.click(), 200); },
        quickAddChecklist() { this.openForm(); this.isCheckboxMode = true; this.checkboxes = [{ text: "", checked: false }]; },

        openForm() {
            this.isFormOpen = true;
            this.showFormatTools = false;
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
        
        truncate(str, n){ return (str && str.length > n) ? str.substr(0, n-1) + '...' : str; },

        editNote(note) {
            this.currentNoteId = note.id;
            this.title = note.title;
            this.noteColor = note.color;
            this.isPinned = note.is_pinned;
            this.tags = [...(note.labels || [])];
            this.imagePreview = note.image_url || null;
            this.reminderTime = note.reminder_time || "";
            this.sharedEmails = ""; 
            this.deadline = note.deadline || "";
            this.status = note.status || "todo";
            
            try {
                const parsed = JSON.parse(note.content);
                if (parsed && parsed.type === 'checklist') {
                    this.isCheckboxMode = true;
                    this.checkboxes = parsed.data;
                    this.content = note.content;
                } else { throw new Error("Not checklist"); }
            } catch (e) {
                this.isCheckboxMode = false;
                this.content = note.content;
                this.$nextTick(() => { const editor = document.getElementById("editor"); if(editor) editor.innerHTML = this.content; });
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
            formData.append("deadline", this.deadline);
            formData.append("status", this.status);

            if (this.imageFile) formData.append("image", this.imageFile);
            formData.append("csrfmiddlewaretoken", this.csrfToken);

            let url = this.urls.create;
            if (isUpdate) url = this.urls.update.replace("00000", this.currentNoteId);

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
            this.deadline = "";
            this.status = "todo";
            clearTimeout(this._timer);
        },
    };
}