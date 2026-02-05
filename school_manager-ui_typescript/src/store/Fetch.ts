export const url = process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:80/' : '/';

export const Get = async (controller: string) => {
    return await fetch(url + controller, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(res => {
            if (res.statusText === 'UNAUTHORIZED') {
                localStorage.clear();
                sessionStorage.clear();
                window.location.replace('/');
            }
            else return res.json();
        })
        .catch(err => console.error(err))
}

export const GetHeader = async (controller: string) => {
    return await fetch(url + controller, {
        method: 'GET',
    })
        .then(res => {
            if (res.statusText === 'UNAUTHORIZED') {
                localStorage.clear();
                sessionStorage.clear();
                window.location.replace('/');
            }
            else return res;
        })
        .catch(err => console.error(err))
}

export const Post = async (controller: string, body: object, withoutJson?: boolean) => {
    return await fetch(url + controller, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    })
        .then(res => withoutJson ? res : res.json())
        .catch(err => console.error(err))
}

export const PostFormData = async (controller: string, formData: BodyInit) => {
    return await fetch(url + controller, {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .catch(err => console.error(err))
}

export const Put = async (controller: string, body: object) => {
    return await fetch(url + controller, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    })
        .then(res => res.json())
        .catch(err => console.error(err))
}

export const Delete = async (controller: string, body: object) => {
    return await fetch(url + controller, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    })
        .then(res => res.json())
        .catch(err => console.error(err))
}