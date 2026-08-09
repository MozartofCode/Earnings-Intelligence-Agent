import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BriefDetail } from './brief-detail';

describe('BriefDetail', () => {
  let component: BriefDetail;
  let fixture: ComponentFixture<BriefDetail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BriefDetail],
    }).compileComponents();

    fixture = TestBed.createComponent(BriefDetail);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
