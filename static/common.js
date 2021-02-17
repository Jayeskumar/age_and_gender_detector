let uploading = false

function lockUploading() {
    uploading = true
    wait.style.display = 'block'
}

function unLockUploading() {
    uploading = false
    wait.style.display = 'none'
}

function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const fileReader = new FileReader()

        fileReader.onload = function (evt) {
            resolve(evt.target.result)
        }
        fileReader.onerror = function (e) {
            reject(e)
        }

        fileReader.readAsDataURL(blob)
    })
}

function getFileFromEvt(e) {
    const files = e.target.files || e.dataTransfer.files
    if (!files.length) {
        return null
    }

    return files[0]
}