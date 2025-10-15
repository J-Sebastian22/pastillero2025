import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';


@Injectable({
  providedIn: 'root'
})
export class Auth {
  
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  registrar(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}registro/`, data);
  }

  login(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}login/`, data);
  }

  guardarUsuario(usuario: any) {
    localStorage.setItem('usuario', JSON.stringify(usuario));
  }

  obtenerUsuario() {
    return JSON.parse(localStorage.getItem('usuario') || 'null');
  }

  cerrarSesion() {
    localStorage.removeItem('usuario');
  }
}