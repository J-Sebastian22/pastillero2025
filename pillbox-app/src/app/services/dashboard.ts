import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';


@Injectable({
  providedIn: 'root'
})
export class Dashboards {
  private apiUrl = `${environment.apiUrl}proximos-horarios/`;

  constructor(private http: HttpClient) {}

  getProximosHorarios(id_usuario: number): Observable<any> {
    return this.http.get(`${this.apiUrl}?id_usuario=${id_usuario}`);
  }
}
